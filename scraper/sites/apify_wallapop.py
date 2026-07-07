"""
Búsqueda en Wallapop vía el Actor de Apify 'igolaizola/wallapop-scraper'.

Al igual que con coches.net, este Actor resuelve por su cuenta el bloqueo
anti-bot de Wallapop, así que solo traducimos input/output.

IMPORTANTE: no conocemos aún con total certeza los nombres exactos de los
campos que devuelve este Actor en cada resultado. Probamos varios nombres
habituales y además IMPRIMIMOS un ejemplo completo del primer resultado en
el log ('ejemplo de item') para poder ajustar en dos minutos si hace falta.
"""
import json
from ..apify_client import run_actor_sync

ACTOR_ID = "igolaizola/wallapop-scraper"


def _extract_price(item):
    price = item.get("price")
    if isinstance(price, dict):
        return price.get("value") or price.get("amount") or price.get("price")
    return price


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
    if items:
        print(f"[apify:wallapop] claves del item: {list(items[0].keys())}")
        print(f"[apify:wallapop] ejemplo de item COMPLETO: {json.dumps(items[0], ensure_ascii=False)}")

    for it in items:
        url = it.get("url") or it.get("webSlug") or it.get("link") or it.get("detailUrl")
        if url and not str(url).startswith("http"):
            url = f"https://es.wallapop.com/item/{url}"
        title = it.get("title") or it.get("name")
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
