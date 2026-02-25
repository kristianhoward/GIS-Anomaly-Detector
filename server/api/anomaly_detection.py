from typing import Optional, Tuple, List

import anthropic
import osmnx
from geopandas import GeoDataFrame
from networkx.classes import MultiDiGraph
from pandas import Series, isna, DataFrame
from shapely import Polygon
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from server.api.claude_client import ClaudeClient
from server.api.constants import DATA_HEADERS, LOCATION_TAGS, ANOMALY_HEADERS
from server.api.utilities import is_geometrical_entry, get_center_of_polygon, to_meters

_CLAUDE_CLIENT = ClaudeClient(anthropic.Anthropic())


def get_location_data(location: str) -> Tuple[GeoDataFrame, MultiDiGraph]:
    return (osmnx.features_from_place(location, tags=LOCATION_TAGS),
            osmnx.graph_from_place(location, network_type="drive"))


class CityData:
    def __init__(self,
                 location_geo: GeoDataFrame,
                 street_graph: MultiDiGraph,
                 ):
        self._full_dataset = to_meters(location_geo)
        _, self._edges = osmnx.graph_to_gdfs(street_graph)
        self._edges = to_meters(self._edges)
        self._street_graph = osmnx.projection.project_graph(street_graph, to_crs=self._edges.crs)
        self._buildings = self._full_dataset[self._full_dataset["building"].notna()]
        self._amenities = self._full_dataset[self._full_dataset['name'].notna()]
        self._amenities = self._amenities.merge(self._get_anomaly_dataframe(self._amenities), on="name", how="left")

    @classmethod
    def from_location(cls, location: str) -> 'CityData':
        return CityData(
            *get_location_data(location)
        )

    @property
    def dataset(self) -> GeoDataFrame:
        return self._full_dataset

    @property
    def street_graph(self) -> MultiDiGraph:
        return self._street_graph

    @property
    def street_edges(self) -> GeoDataFrame:
        return self._edges

    @property
    def amenities(self):
        return self._amenities

    @property
    def buildings(self) -> GeoDataFrame:
        return self._buildings

    @staticmethod
    def _anomalies_detected(dataframe: DataFrame, percent: float = 0.05) -> DataFrame:
        ids = dataframe[DATA_HEADERS[0]]

        vals_only = dataframe[DATA_HEADERS].drop(columns=[DATA_HEADERS[0]])
        vals_only = vals_only.fillna(0)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(vals_only)

        # Train model
        model = IsolationForest(
            n_estimators=100,
            contamination=percent,
            random_state=42
        )

        model.fit(X_scaled)

        scores = model.decision_function(X_scaled)
        preds = model.predict(X_scaled)

        is_anomaly = (preds == -1).astype(int)

        results = DataFrame({
            ANOMALY_HEADERS[0]: ids,
            ANOMALY_HEADERS[1]: scores,
            ANOMALY_HEADERS[2]: is_anomaly
        })

        return results

    def _get_anomaly_dataframe(self, amenities: GeoDataFrame) -> GeoDataFrame:
        data = {DATA_HEADERS[0]: [], DATA_HEADERS[1]: [], DATA_HEADERS[2]: [], DATA_HEADERS[3]: [], DATA_HEADERS[4]: []}

        for _, location in amenities.iterrows():
            if isna(location['name']):
                continue

            nearest_st = self.get_nearest_street(location)
            nearest_st_distance = (
                nearest_st["geometry"].distance(location["geometry"]) if nearest_st is not None else 0
            )

            _, nearest_location_distance = self.get_nearest_location(location)
            nearest_location_distance = nearest_location_distance or 0

            if isinstance(location['name'], float):
                continue
            else:
                name = location['name']

            data[DATA_HEADERS[0]].append(name)
            data[DATA_HEADERS[1]].append(nearest_st_distance)
            data[DATA_HEADERS[2]].append(nearest_location_distance)
            data[DATA_HEADERS[3]].append(len(self.get_nearby_locations(location, meters=500)))
            data[DATA_HEADERS[4]].append(len(self.intersects_other_locations(location)))

        return GeoDataFrame(data)

    def get_place_of_interest(self, location_name: str) -> List[Series]:
        return [self._amenities.iloc[x] for x in range(len(self._amenities)) if
                location_name == self._amenities.iloc[x]['name']]

    def get_nearest_street(self, location: Series) -> Optional[Series]:
        if not is_geometrical_entry(location):
            return None

        p = location["geometry"]

        if isinstance(location["geometry"], Polygon):
            p = get_center_of_polygon(location)

        u, v, key = osmnx.distance.nearest_edges(
            self._street_graph,
            X=p.x,
            Y=p.y
        )

        nearest = self._edges.loc[(u, v, key)]

        return nearest

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
            p = get_center_of_polygon(place)

        potential_matches_idx = list(self._buildings.sindex.query(p, predicate='intersects'))
        intersections = [self._buildings.iloc[idx] for idx in potential_matches_idx
                         if self._buildings.geometry.iloc[idx].contains(p)]

        return intersections

    def ai_anomaly_response(self, percent: float = 0.05, nsmallest: int = 5) -> GeoDataFrame:
        anomalies = self._amenities.merge(self._anomalies_detected(self._amenities, percent=percent), on="name", how="left").nsmallest(nsmallest, "anomaly_score")
        return _CLAUDE_CLIENT.build_response(anomalies)
