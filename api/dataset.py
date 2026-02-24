import json
from types import NoneType

import requests
from typing import Union, Dict, List
from pandas import Series


class AnomalyDetectorConn:
    def __init__(self, conn: str = "http://127.0.0.1:8000/") -> None:
        self._connection = conn

    def connected(self) -> bool:
        response = requests.get(self._connection)
        if response.status_code != 200:
            return False

        return response.json() == {"status": "API running"}

    def get_city_data(self, city: str) -> Dict[str, Dict]:
        response = requests.get(self._connection + "/osmnx", params={"city": city})

        return response.json()

    def get_all_dataframes(self, city: str) -> Dict[str, Dict]:
        response = requests.get(self._connection + "/debug", params={"city": city})

        return response.json()

    def get_place_data(self, *, location: str, city: str) -> List[Dict[str, Union[str, Series]]]:
        response = requests.get(self._connection + "/place", params={"city": city, "location": location})

        return response.json()

    def get_nearest_place_data(self, *, location: str, city: str, loc_id: int = 1) -> Dict[str, Union[str, Series]]:
        response = requests.get(self._connection + "/nearest",
                                params={"city": city, "location": location, "loc_id": loc_id})

        return response.json()

    def get_anomaly_data(self, location: str) -> List[Dict[str, Union[str, Union[str, NoneType, int, float]]]]:
        response = requests.get(self._connection + "/anomaly", params={"city": location})

        raw = response.json()
        geojson = json.loads(raw) if isinstance(raw, str) else raw
        return geojson.get("features", [])
