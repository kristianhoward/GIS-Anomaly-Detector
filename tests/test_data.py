import tempfile
from pathlib import Path

import pytest
from pandas import Series

from api.dataset import CityData
from conftest import city_data_frame


@pytest.fixture(scope="session")
def place(city_data_frame: CityData) -> Series:
    return city_data_frame.get_place_of_interest("Calvary Chapel Beaumont")[0]


def test_get_dataset(city_data_frame: CityData) -> None:
    assert len(city_data_frame.get_places_of_interest_names()) > 0

def test_all_places_of_interest_names(city_data_frame: CityData) -> None:
    for name in city_data_frame.get_places_of_interest_names():
        assert isinstance(name, str)

def test_get_centralized_point_of_dataset(city_data_frame: CityData) -> None:
    assert city_data_frame.get_centroid()

def test_get_place_of_interest(city_data_frame: CityData) -> None:
    assert len(city_data_frame.get_place_of_interest("Calvary Chapel Beaumont")) > 0

def test_get_nearest_street_of_church(city_data_frame: CityData, place: Series) -> None:
    assert city_data_frame.get_nearest_street_distance(place) > 0

def test_get_nearest_location(city_data_frame: CityData, place: Series) -> None:
    assert city_data_frame.get_nearest_location(place)[0]['name'] == 'Starlight Elementary School'

def test_get_nearby_locations(city_data_frame: CityData, place: Series) -> None:
    assert len(city_data_frame.get_nearby_locations(place, meters=500)) == 1

@pytest.mark.xfail(reason="Expected behavior")
def test_intersection_of_data() -> None:
    city_data_frame = CityData("Anaheim, California, USA")
    for location in [x[1] for x in city_data_frame.get_geo_dataframe().iterrows()]:
        assert len(city_data_frame.intersects_other_locations(location)) < 2

def test_csv(city_data_frame: CityData) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.csv"
        city_data_frame.to_csv(path)

        assert path.exists()

def test_csv_local(city_data_frame: CityData) -> None:
    path = Path.cwd() / "test.csv"
    city_data_frame.to_csv(path)

    assert path.exists()

def test_anomaly_detection(city_data_frame: CityData) -> None:
    path = Path.cwd() / "anomaly.csv"
    city_data_frame.detect_anomalies_csv(path)
