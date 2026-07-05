"""
Búsqueda en coches.net vía el Actor de Apify 'rastriq/cochesnet-spain'.

Este Actor ya resuelve por su cuenta las protecciones anti-bot de coches.net,
así que aquí solo nos encargamos de mandarle el input correcto y traducir
su salida al formato común que usa nuestro panel.

IMPORTANTE: no conocemos aún con total certeza los nombres exactos de los
campos que devuelve este Actor en cada resultado (título, precio, url...).
Por eso probamos varios nombres habituales, y además IMPRIMIMOS un ejemplo
completo del primer resultado en el log (ver 'ejemplo de item') — si algún
campo no se detecta bien, con ese ejemplo se ajusta en dos minutos.
"""
import json
from ..apify_client import run_actor_sync

ACTOR_ID = "rastriq/cochesnet-spain"


def _extract_price(item):
    price = item.get("price")
    if isinstance(price, dict):
        return price.get("value") or price.get("amount") or price.get("price")
    return price


def run_search(session, params: dict, delay: float, token: str):
    input_data = {}
    if params.get("make"):
        input_data["make"] = params["make"]
    if params.get("model"):
        input_data["model"] = params["model"]
    if params.get("fuel"):
        input_data["fuel"] = params["fuel"]
    if params.get("min_price") is not None:
        input_data["minPrice"] = params["min_price"]
    if params.get("max_price") is not None:
        input_data["maxPrice"] = params["max_price"]
    if params.get("min_year") is not None:
        input_data["minYear"] = params["min_year"]
    if params.get("max_year") is not None:
        input_data["maxYear"] = params["max_year"]
    input_data["maxItems"] = params.get("max_items", 50)
    input_data["maxPages"] = params.get("max_pages", 3)

    results = []
    if not token:
        print("[apify:coches_net] AVISO: no hay token de Apify configurado, se salta esta búsqueda.")
        return results

    try:
        items = run_actor_sync(token, ACTOR_ID, input_data)
    except Exception as e:
        print(f"[apify:coches_net] ERROR ejecutando el Actor: {e}")
        return results

    print(f"[apify:coches_net] items recibidos: {len(items)}")
    if items:
        print(f"[apify:coches_net] ejemplo de item: {json.dumps(items[0], ensure_ascii=False)[:1000]}")

    for it in items:
        url = it.get("url") or it.get("adUrl") or it.get("link") or it.get("detailUrl")
        title = it.get("title") or it.get("name") or it.get("adTitle")
        price = _extract_price(it)
        if not url:
            continue
        results.append({"url": url, "title": title, "price": price})

    return results
