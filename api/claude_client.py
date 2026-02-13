import json
from typing import List, Union, Dict

from anthropic import Client, HUMAN_PROMPT, AI_PROMPT
from anthropic.types import TextBlock

from api.constants import CSV_HEADERS

system_prompt = f"""
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
        - n = {CSV_HEADERS[0]}, The name of the location
        - l = {CSV_HEADERS[1]}, The number of locations surrounding it within (500 meters)
        - r = {CSV_HEADERS[2]}, its distance to the road in meters
        - b = {CSV_HEADERS[3]}, its distance to the nearest building in meters
        - i = {CSV_HEADERS[4]}, its position intersects multiple buildings
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

    def explain_anomaly(self, location_data: List[Dict[str, Union[int, float]]]) -> List[Dict[str, str]]:
        msg = self._send_message(
            f"{system_prompt}\n\n{HUMAN_PROMPT} {self._user_prompt(self._shrink_json_data(location_data))} {AI_PROMPT}")
        return json.loads(msg[0].text.replace("json", "").replace("`", ""))

    @staticmethod
    def _shrink_json_data(location_data: List[Dict[str, Union[int, float]]]) -> List[Dict[str, Union[int, float]]]:
        key_map = {
            CSV_HEADERS[0]: "n",
            CSV_HEADERS[1]: "l",
            CSV_HEADERS[2]: "r",
            CSV_HEADERS[3]: "b",
            CSV_HEADERS[4]: "i",
        }
        return [{key_map.get(k, k): v for k, v in d.items()} for d in location_data]
