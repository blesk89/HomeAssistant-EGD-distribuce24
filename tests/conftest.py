"""Sdílené fixtures pro testy EGD Power Data integrace."""
import pytest
from unittest.mock import patch, MagicMock


MOCK_TOKEN = "test_access_token_12345"

MOCK_DATA_RESPONSE = [
    {
        "ean/eic": "859182400208547692",
        "profile": "ICC1",
        "units": "KW",
        "total": 4,
        "data": [
            {"timestamp": "2026-04-09T00:00:00.000Z", "value": 100, "status": "IU012"},
            {"timestamp": "2026-04-09T00:15:00.000Z", "value": 200, "status": "IU012"},
            {"timestamp": "2026-04-09T00:30:00.000Z", "value": 300, "status": "IU012"},
            {"timestamp": "2026-04-09T00:45:00.000Z", "value": 400, "status": "IU012"},
        ],
    }
]

MOCK_TOKEN_RESPONSE = {
    "access_token": MOCK_TOKEN,
    "token_type": "bearer",
    "expires": 14425000,
}

CONFIG = {
    "platform": "egdczpowerdata",
    "client_id": "test_client_id",
    "client_secret": "test_client_secret",
    "ean": "859182400208547692",
    "days": 1,
}


@pytest.fixture
def mock_token_request():
    """Mock volání pro získání tokenu."""
    with patch("requests.Session.post") as mock_post:
        response = MagicMock()
        response.json.return_value = MOCK_TOKEN_RESPONSE
        response.raise_for_status = MagicMock()
        mock_post.return_value = response
        yield mock_post


@pytest.fixture
def mock_data_request():
    """Mock volání pro stažení dat."""
    with patch("requests.Session.get") as mock_get:
        response = MagicMock()
        response.json.return_value = MOCK_DATA_RESPONSE
        response.status_code = 200
        response.raise_for_status = MagicMock()
        mock_get.return_value = response
        yield mock_get


@pytest.fixture
def mock_api(mock_token_request, mock_data_request):
    """Mock celého API (token + data)."""
    return {"token": mock_token_request, "data": mock_data_request}
