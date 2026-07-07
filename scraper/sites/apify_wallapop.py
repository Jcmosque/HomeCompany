"""
Búsqueda en Wallapop vía el Actor de Apify 'igolaizola/wallapop-scraper'.

Al igual que con coches.net, este Actor resuelve por su cuenta el bloqueo
anti-bot de Wallapop, así que solo traducimos input/output.
"""
import json
from ..apify_client import run_actor_sync

ACTOR_ID = "igolaizola/wallapop-scraper"


def _extract_price(item):
    price = item.get("price")
    if isinstance(price, dict):
        cash = price.get("cash")
        if isinstance(cash, dict):
            return cash.get("amount")
        return price.get("value") or price.get("amount")
    return price


def _extract_url(item):
    slug = item.get("web_slug")
    if slug:
        return f"https://es.wallapop.com/item/{slug}"
    details = item.get("_details") or {}
    share_url = details.get("share_url")
    if share_url:
        return share_url.split("?")[0]
    return None


def run_search(session, query: str, max_price, location: str, delay: float, token: str,
               postal_code=None, max_items=50, distance="", order_by="most_relevance",
               fetch_details=True):
    input_data = {
        "query": query,
        "maxItems": max_items,
        "distance": distance,
        "orderBy": order_by,
        "fetchDetails": fetch_details,
    }
    if postal_code:
        input_data["postalCode"] = postal_code

    results = []
    if not token:
        print("[apify:wallapop] AVISO: no hay token de Apify configurado, se salta esta búsqueda.")
        return results

    try:
        items = run_actor_sync(token, ACTOR_ID, input_data)
    except Exception as e:
        print(f"[apify:wallapop] ERROR ejecutando el Actor: {e}")
        return results

    print(f"[apify:wallapop] items recibidos: {len(items)}")

    for it in items:
        url = _extract_url(it)
        title = it.get("title")
        price = _extract_price(it)

        # Filtramos por precio máximo aquí, ya que el Actor no lo admite como parámetro de entrada
        if max_price is not None and price is not None:
            try:
                if float(price) > float(max_price):
                    continue
            except (TypeError, ValueError):
                pass

        if not url:
            continue
        results.append({"url": url, "title": title, "price": price})

    return results
