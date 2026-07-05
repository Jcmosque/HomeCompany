"""
Utilidades compartidas por todos los scrapers de sitios.
"""
import time
import re
import requests

DEFAULT_TIMEOUT = 15


def get_session(user_agent: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": user_agent,
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    return s


def fetch(session: requests.Session, url: str, delay: float = 3.0, **kwargs):
    """Hace un GET respetuoso: espera `delay` segundos antes de la petición."""
    time.sleep(delay)
    resp = session.get(url, timeout=DEFAULT_TIMEOUT, **kwargs)
    resp.raise_for_status()
    return resp


def parse_price(text: str):
    """Convierte '12.345 €' o '12345€' o '12,345.00 EUR' en un float. Devuelve None si no encuentra número."""
    if not text:
        return None
    # nos quedamos solo con dígitos, puntos y comas
    cleaned = re.sub(r"[^\d.,]", "", text)
    if not cleaned:
        return None
    # formato español: puntos = miles, coma = decimales
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None
