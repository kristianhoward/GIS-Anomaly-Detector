import math
from pathlib import Path
from typing import List, Optional, Tuple

import osmnx
from geopandas import GeoDataFrame
from pandas import Series, DataFrame
from shapely import Point, Polygon

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from api.constants import CSV_HEADERS, LOCATION_TAGS, ANOMALY_HEADERS

osmnx.settings.use_cache = True


class CityData:
    def __init__(self, location: str) -> None:
        self._dataset = self._to_meters(osmnx.features_from_place(location, tags=LOCATION_TAGS))
        self._street_graph = osmnx.graph_from_place(location, network_type="drive")
        _, self._edges = osmnx.graph_to_gdfs(self._street_graph)
        self._edges = self._to_meters(self._edges)
        self._buildings = self._dataset[self._dataset["building"].notna()]
        self._amenities = self._dataset[self._dataset['name'].notna()]
        self._amenities = self._amenities.merge(self._get_location_dataframe(), on="name", how="left")

    @staticmethod
    def _to_meters(data: GeoDataFrame) -> GeoDataFrame:
        return data.to_crs(data.estimate_utm_crs())

    @staticmethod
    def is_geometrical_entry(location: Series) -> bool:
        try:
            return hasattr(location['geometry'], 'x') and hasattr(location['geometry'], 'y')
        except (AttributeError, KeyError):
            return False

    @staticmethod
    def get_center_of_polygon(location: Series) -> Point:
        p = location['geometry']
        assert isinstance(p, Polygon)

        return p.centroid

    def get_global_dataset(self) -> GeoDataFrame:
        return self._dataset

    def get_centroid(self) -> Point:
        return self._dataset.union_all().centroid

    def get_places_of_interest_names(self) -> List[str]:
        result = []
        for x in range(len(self._amenities)):
            name = self._amenities.iloc[x]['name']
            if isinstance(name, float):
                result.append(str(name) if math.isnan(name) else name)
            else:
                result.append(name)
        return result

    def get_place_of_interest(self, location_name: str) -> List[Series]:
        return [self._amenities.iloc[x] for x in range(len(self._amenities)) if
                location_name == self._amenities.iloc[x]['name']]

    def get_nearest_street_distance(self, location: Series) -> Optional[int]:
        if not self.is_geometrical_entry(location):
            return None

        return min(self._edges.geometry.iloc[x].distance(location['geometry']) for x in range(len(self._edges)))

    def get_nearby_locations(self, location: Series, *, meters: int) -> List[Series]:
        return [self._amenities.iloc[x] for x in range(len(self._amenities)) if
                self._amenities.geometry.iloc[x].distance(location['geometry']) < meters and self._amenities.iloc[x][
                    'name'] != location['name']]

    def get_nearest_location(self, location: Series) -> Tuple[Optional[Series], Optional[int]]:
        min_location_distance = min(
            self._amenities.geometry.iloc[x].distance(location['geometry']) for x in range(len(self._amenities)) if
            self._amenities.geometry.iloc[x] != location['geometry'])
        min_location = [self._amenities.iloc[x] for x in range(len(self._amenities)) if
                        self._amenities.geometry.iloc[x].distance(location['geometry']) == min_location_distance][0]

        return min_location, min_location_distance

    def intersects_other_locations(self, place: Series) -> List[Series]:
        p = place['geometry']

        if isinstance(p, Polygon):
            p = self.get_center_of_polygon(place)

        # Use spatial index for much faster lookups
        potential_matches_idx = list(self._buildings.sindex.query(p, predicate='intersects'))
        intersections = [self._buildings.iloc[idx] for idx in potential_matches_idx
                         if self._buildings.geometry.iloc[idx].contains(p)]

        return intersections

    def _get_location_dataframe(self) -> DataFrame:
        data = {CSV_HEADERS[0]: [], CSV_HEADERS[1]: [], CSV_HEADERS[2]: [], CSV_HEADERS[3]: [], CSV_HEADERS[4]: []}

        for location in [x[1] for x in self._amenities.iterrows()]:
            nearest_st_distance = y if (y := self.get_nearest_street_distance(location)) else 0
            nearest_location_distance = y if (y := self.get_nearest_location(location)[1]) else 0
            if isinstance(location['name'], float):
                continue
            else:
                name = location['name']
            data[CSV_HEADERS[0]].append(name)
            data[CSV_HEADERS[1]].append(nearest_st_distance)
            data[CSV_HEADERS[2]].append(nearest_location_distance)
            data[CSV_HEADERS[3]].append(len(self.get_nearby_locations(location, meters=500)))
            data[CSV_HEADERS[4]].append(len(self.intersects_other_locations(location)))

        return DataFrame(data)

    def to_csv(self, path: Path) -> None:
        self._amenities.to_csv(path, chunksize=100_000)

    @staticmethod
    def _anomalies_detected(dataframe: DataFrame, percent: float = 0.05) -> DataFrame:
        ids = dataframe[CSV_HEADERS[0]]

        vals_only = dataframe[CSV_HEADERS].drop(columns=[CSV_HEADERS[0]])

        # Fill missing values
        vals_only = vals_only.fillna(0)

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(vals_only)

        # Train model
        model = IsolationForest(
            n_estimators=100,
            contamination=percent,  # assume 5% anomalies
            random_state=42
        )

        model.fit(X_scaled)

        # Get anomaly scores
        scores = model.decision_function(X_scaled)
        preds = model.predict(X_scaled)

        # IsolationForest: -1 = anomaly, 1 = normal
        is_anomaly = (preds == -1).astype(int)

        # Save results
        results = DataFrame({
            ANOMALY_HEADERS[0]: ids,
            ANOMALY_HEADERS[1]: scores,
            ANOMALY_HEADERS[2]: is_anomaly
        })

        return results

    def detect_anomalies(self, percent: float = 0.05) -> DataFrame:
        return self._amenities.merge(self._anomalies_detected(self._amenities, percent=percent), on="name", how="left")
