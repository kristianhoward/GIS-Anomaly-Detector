import pytest

from api.dataset import AnomalyDetectorConn


@pytest.fixture(scope="session")
def anomaly_detector():
    return AnomalyDetectorConn()
