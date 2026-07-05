"""
Scraper para Wallapop.

Wallapop carga los anuncios vía llamadas a su API interna (la misma que usa
su web/app). Usamos esos endpoints en vez de parsear HTML porque son más
estables, pero AL SER NO OFICIALES pueden cambiar sin aviso.
Si dejan de funcionar, hay que inspeccionar la pestaña "Network" del
navegador en wallapop.com para encontrar la nueva URL del endpoint.
"""
from ..utils import fetch, parse_price

SITE_NAME = "wallapop"

SEARCH_API = "https://api.wallapop.com/api/v3/general/search"
ITEM_API = "https://api.wallapop.com/api/v3/items/{item_id}"


def check_listing(session, url, delay):
    """Comprueba un anuncio concreto a partir de su URL pública."""
    item_id = url.rstrip("/").split("-")[-1]
    try:
        resp = fetch(session, ITEM_API.format(item_id=item_id), delay=delay)
        data = resp.json()
    except Exception:
        return {"active": False, "price": None, "title": None}

    if not data or data.get("flags", {}).get("banned") or data.get("flags", {}).get("sold"):
        return {"active": False, "price": data.get("price", {}).get("amount") if data else None,
                "title": data.get("title") if data else None}

    return {
        "active": True,
        "price": data.get("price", {}).get("amount"),
        "title": data.get("title"),
    }


def run_search(session, query: str, max_price, location: str, delay: float):
    params = {
        "keywords": query,
        "latitude": "40.4168",   # AJUSTAR: coordenadas por defecto (Madrid). Cambia si buscas en otra ciudad.
        "longitude": "-3.7038",
        "max_sale_price": max_price,
        "order_by": "newest",
    }
    results = []
    try:
        resp = fetch(session, SEARCH_API, delay=delay, params=params)
        data = resp.json()
    except Exception:
        return results

    for item in data.get("search_objects", []):
        results.append({
            "url": f"https://es.wallapop.com/item/{item.get('web_slug', item.get('id'))}",
            "title": item.get("title"),
            "price": parse_price(str(item.get("price"))),
        })
    return results
