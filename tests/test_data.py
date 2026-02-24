import pytest

from typing import Dict
from shapely.geometry import shape
from api.dataset import AnomalyDetectorConn

_CITY = "Beaumont, CA, USA"
_PLACE = "Calvary Chapel Beaumont"


def test_get_dataset(anomaly_detector: AnomalyDetectorConn) -> None:
    assert len(anomaly_detector.get_city_data(city=_CITY)) > 0


def test_get_place_of_interest(anomaly_detector: AnomalyDetectorConn) -> None:
    assert len(anomaly_detector.get_place_data(location=_PLACE, city=_CITY)) > 0


class TestNearbyElements:
    @pytest.fixture(scope="class")
    def nearest_data(self, anomaly_detector: AnomalyDetectorConn) -> Dict:
        return anomaly_detector.get_nearest_place_data(location=_PLACE, city=_CITY)

    def test_get_nearest_street_distance_from_church(self, nearest_data: Dict) -> None:
        assert nearest_data['street']['name'] == "Starlight Avenue"
        assert shape(nearest_data['street']['geometry']).distance(
            shape(nearest_data['place']['geometry'])) == 143.61859753791583

    def test_get_nearest_location(self, nearest_data: Dict) -> None:
        assert nearest_data['location']['name'] == 'Starlight Elementary School'

    def test_get_nearby_locations(self, nearest_data: Dict) -> None:
        assert len(nearest_data['nearby']) == 1

    def test_intersection_of_data(self, nearest_data: Dict) -> None:
        assert len(nearest_data['intersections']) == 0
