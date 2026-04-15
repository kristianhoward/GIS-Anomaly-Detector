import pytest
from fastapi.testclient import TestClient
from server.main import app


class _TestConn:
    """Thin wrapper around TestClient with the same interface used by tests."""

    def __init__(self, client: TestClient) -> None:
        self._client = client

    def get_city_data(self, city: str):
        return self._client.get("/osmnx", params={"city": city}).json()

    def get_place_data(self, *, location: str, city: str):
        return self._client.get("/place", params={"city": city, "location": location}).json()

    def get_nearest_place_data(self, *, location: str, city: str, loc_id: int = 1):
        return self._client.get(
            "/nearest",
            params={"city": city, "location": location, "loc_id": loc_id},
        ).json()


@pytest.fixture(scope="session")
def anomaly_detector():
    with TestClient(app) as client:
        yield _TestConn(client)
