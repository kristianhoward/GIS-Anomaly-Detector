import pytest
from requests import session

from api.dataset import CityData


@pytest.fixture(scope="session")
def city_data_frame() -> CityData:  # what if i wanted to scale this by providing my own data?
    return CityData("Beaumont, California, USA")
