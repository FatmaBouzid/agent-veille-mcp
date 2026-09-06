"""
On mocke httpx.get pour ne JAMAIS dépendre d'un vrai appel réseau dans les
tests — un test qui dépend d'Open-Meteo serait flaky (échoue si le service
est down, lent, ou si tu es hors ligne) et lent (CI plus long inutilement).
"""

from unittest.mock import MagicMock, patch

from agent_veille.tools.external_api_tool import get_current_weather


def _mock_response(json_data: dict) -> MagicMock:
    mock = MagicMock()
    mock.json.return_value = json_data
    mock.raise_for_status.return_value = None
    return mock


@patch("agent_veille.tools.external_api_tool.httpx.get")
def test_get_current_weather_success(mock_get):
    # premier appel (géocodage), puis deuxième (météo) — dans cet ordre exact
    mock_get.side_effect = [
        _mock_response({"results": [{"latitude": 34.74, "longitude": 10.76}]}),
        _mock_response({"current": {"temperature_2m": 28.5, "wind_speed_10m": 12.0}}),
    ]

    result = get_current_weather.invoke({"city_name": "Sfax"})

    assert "28.5°C" in result
    assert "Sfax" in result


@patch("agent_veille.tools.external_api_tool.httpx.get")
def test_get_current_weather_city_not_found(mock_get):
    mock_get.return_value = _mock_response({"results": []})

    result = get_current_weather.invoke({"city_name": "VilleInexistanteXYZ"})

    assert "introuvable" in result

def test_get_current_weather_rejects_empty_city():
    result = get_current_weather.invoke({"city_name": " "})
    assert "Entrée invalide" in result