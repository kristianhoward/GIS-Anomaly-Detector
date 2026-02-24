import json
from typing import List, Union, Dict

from anthropic import Client, HUMAN_PROMPT, AI_PROMPT
from anthropic.types import TextBlock
from geopandas.geodataframe import GeoDataFrame
from pandas import DataFrame

from server.api.constants import DATA_HEADERS

_SYSTEM_PROMPT = f"""
        You are a geospatial data quality assistant.

        This has been flagged as anomalous.
        Based on the following features, your task is:
        
        1. Analyze the numeric features of a flagged business location.
        2. Determine if it is suspicious.
        3. Return a JSON object only, with keys:
           - "risk_level": "low", "medium", or "high"
           - "explanation": a short human-readable explanation (<20 words)
           - "suggested_check": what a GIS analyst should verify

        Feature keys:
        - n = {DATA_HEADERS[0]}, The name of the location
        - l = {DATA_HEADERS[1]}, The number of locations surrounding it within (500 meters)
        - r = {DATA_HEADERS[2]}, its distance to the road in meters
        - b = {DATA_HEADERS[3]}, its distance to the nearest building in meters
        - i = {DATA_HEADERS[4]}, its position intersects multiple buildings
"""


class ClaudeClient:
    def __init__(self, client: Client) -> None:
        self._client = client

    @staticmethod
    def _user_prompt(features_json: List[Dict[str, Union[int, float]]]) -> str:
        return f"""
        Analyze the following anomalies and return a JSON array with the structure defined in the system prompt:
        
        {features_json}
        """

    def _send_message(self, prompt: str) -> List[TextBlock]:
        tokens_cost = self._client.messages.count_tokens(
            model="claude-opus-4-6",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        message = self._client.messages.create(
            model="claude-opus-4-6",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        return message.content

    def append_explanations(self, anomaly_frame: GeoDataFrame) -> GeoDataFrame:
        claude_data = GeoDataFrame(
            self.explain_anomalies(anomaly_frame[DATA_HEADERS + ['geometry']].to_geo_dict()['features']))

        return anomaly_frame.merge(claude_data, on="n", how="left")

    @staticmethod
    def parse_anomaly_data(anomalies: GeoDataFrame) -> List[Dict[str, Union[int, float]]]:
        key_map = {
            DATA_HEADERS[0]: "n",
            DATA_HEADERS[1]: "l",
            DATA_HEADERS[2]: "r",
            DATA_HEADERS[3]: "b",
            DATA_HEADERS[4]: "i",
        }
        anomaly_cols = [col for col in DATA_HEADERS if col in key_map]
        return [
            {key_map[col]: row[col] for col in anomaly_cols}
            for _, row in anomalies.iterrows()
        ]

    def build_response(self, anomalies: GeoDataFrame) -> GeoDataFrame:
        anomaly_data = self.parse_anomaly_data(anomalies)

        response = self._send_message(
            f"{_SYSTEM_PROMPT}\n\n{HUMAN_PROMPT} {self._user_prompt(anomaly_data)} {AI_PROMPT}")
        ai_assessments = json.loads(response[0].text.replace("json", "").replace("`", ""))

        assessments_df = DataFrame(ai_assessments, index=anomalies.index)
        return anomalies.join(assessments_df)

    @staticmethod
    def _shrink_json_data(location_data: List[Dict[str, Union[int, float]]]) -> List[Dict[str, Union[int, float]]]:
        key_map = {
            DATA_HEADERS[0]: "n",
            DATA_HEADERS[1]: "l",
            DATA_HEADERS[2]: "r",
            DATA_HEADERS[3]: "b",
            DATA_HEADERS[4]: "i",
        }
        return [{key_map.get(k, k): v for k, v in d.items()} for d in location_data]
