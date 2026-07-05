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
    # Parámetros confirmados observando la URL real de búsqueda en es.wallapop.com:
    # https://es.wallapop.com/search?category_id=100&max_sale_price=...&keywords=...&order_by=most_relevance
    params = {
        "keywords": query,
        "category_id": 100,          # 100 = Coches
        "max_sale_price": max_price,
        "order_by": "most_relevance",
    }
    results = []
    try:
        resp = fetch(session, SEARCH_API, delay=delay, params=params)
        data = resp.json()
    except Exception as e:
        print(f"[wallapop] ERROR en la petición: {e}")
        return results

    n_items = len(data.get("search_objects", []))
    print(f"[wallapop] status={resp.status_code} items_encontrados={n_items}")

    for item in data.get("search_objects", []):
        results.append({
            "url": f"https://es.wallapop.com/item/{item.get('web_slug', item.get('id'))}",
            "title": item.get("title"),
            "price": parse_price(str(item.get("price"))),
        })
    return results
