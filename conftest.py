import anthropic
import pytest
from anthropic import Client

from api.claude_client import ClaudeClient
from api.dataset import CityData


@pytest.fixture(scope="session")
def city_data_frame() -> CityData:
    return CityData("Beaumont, California, USA")


@pytest.fixture(scope="session")
def claude_client() -> ClaudeClient:
    return ClaudeClient(anthropic.Anthropic())
