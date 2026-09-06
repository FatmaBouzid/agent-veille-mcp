"""
Tool météo via Open-Meteo — aucune clé API requise.

Deux appels HTTP sont nécessaires :
1. géocodage : nom de ville -> latitude/longitude (API Open-Meteo dédiée)
2. prévisions : latitude/longitude -> météo actuelle

Pourquoi deux appels plutôt qu'un : Open-Meteo sépare volontairement les
deux services (géocodage et météo) pour rester rapide et sans authentification
sur chacun. C'est une contrainte de l'API, pas un choix de design de notre part.
"""

import httpx
from langchain_core.tools import tool

from agent_veille.config import settings
from agent_veille.guardrails.validators import validate_input, with_fallback
from agent_veille.tools.schemas import WeatherInput

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def _geocode_city(city_name: str) -> tuple[float, float] | None:
    """Convertit un nom de ville en (latitude, longitude). Retourne None si introuvable."""
    response = httpx.get(
        GEOCODING_URL,
        params={"name": city_name, "count": 1, "language": "fr"},
        timeout=10.0,
    )
    response.raise_for_status()
    data = response.json()

    results = data.get("results")
    if not results:
        return None

    first = results[0]
    return first["latitude"], first["longitude"]


def _fetch_current_weather(latitude: float, longitude: float) -> dict:
    """Récupère la météo actuelle pour des coordonnées données."""
    response = httpx.get(
        settings.open_meteo_base_url,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,wind_speed_10m,weather_code",
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()["current"]





@with_fallback("Le service météo est momentanément indisponible.")
def _get_current_weather_impl(city_name: str) -> str:
    coordinates = _geocode_city(city_name)
    if coordinates is None:
        return f"Ville '{city_name}' introuvable."

    latitude, longitude = coordinates
    weather = _fetch_current_weather(latitude, longitude)

    return (
        f"Météo actuelle à {city_name} : "
        f"{weather['temperature_2m']}°C, "
        f"vent à {weather['wind_speed_10m']} km/h."
    )


@tool
def get_current_weather(city_name: str) -> str:
    """
    Donne la météo actuelle (température, vent) pour une ville donnée.
    Utilise ce tool uniquement pour des questions sur la météo ou le climat
    actuel d'un lieu précis, PAS pour des questions techniques ou documentaires.
    """
    validated = validate_input(WeatherInput, {"city_name": city_name})
    if isinstance(validated, str):
        return validated

    return _get_current_weather_impl(validated.city_name)