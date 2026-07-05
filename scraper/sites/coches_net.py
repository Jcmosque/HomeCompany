"""
Scraper para coches.net.

IMPORTANTE: coches.net puede cambiar su HTML en cualquier momento.
Los selectores de abajo están marcados con "AJUSTAR SI CAMBIA LA WEB":
si algo deja de funcionar, lo primero es revisar esos puntos con las
herramientas de desarrollador del navegador (Inspeccionar elemento).
"""
from bs4 import BeautifulSoup
from ..utils import fetch, parse_price

SITE_NAME = "coches_net"


def check_listing(session, url, delay):
    """Comprueba un anuncio concreto: devuelve dict con precio, título y si sigue activo."""
    try:
        resp = fetch(session, url, delay=delay)
    except Exception:
        return {"active": False, "price": None, "title": None}

    soup = BeautifulSoup(resp.text, "lxml")

    title_el = soup.select_one("h1")
    title = title_el.get_text(strip=True) if title_el else None

    price = None
    price_el = soup.select_one("[class*='Price'], [data-testid*='price'], .mt-PriceRow-price")
    if price_el:
        price = parse_price(price_el.get_text())

    active = title is not None
    return {"active": active, "price": price, "title": title}


def run_search(session, params: dict, delay: float):
    """Ejecuta una búsqueda por criterios y devuelve lista de anuncios encontrados."""
    # URL y parámetros confirmados observando una búsqueda real en coches.net:
    # https://www.coches.net/search/?OfferType=0&MaxPrice=30000&arrProvince=28&MakeIds[0]=7&ModelIds[0]=0
    base = "https://www.coches.net/search/"

    query = {"OfferType": 0}
    if params.get("marca_id") is not None:
        query["MakeIds[0]"] = params["marca_id"]
    if params.get("modelo_id") is not None:
        query["ModelIds[0]"] = params["modelo_id"]
    if params.get("precio_max"):
        query["MaxPrice"] = params["precio_max"]
    if params.get("provincia_id") is not None:
        query["arrProvince"] = params["provincia_id"]

    results = []
    try:
        resp = fetch(session, base, delay=delay, params=query)
    except Exception as e:
        print(f"[coches_net] ERROR en la petición: {e}")
        return results

    print(f"[coches_net] status={resp.status_code} url_final={resp.url} bytes={len(resp.text)}")

    # DIAGNÓSTICO TEMPORAL: guardamos el HTML recibido para poder inspeccionarlo.
    try:
        import os
        os.makedirs("debug", exist_ok=True)
        with open("debug/coches_net_response.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
    except Exception:
        pass

    soup = BeautifulSoup(resp.text, "lxml")

    cards = soup.select("article, [class*='CardListing'], [data-ad-id]")
    print(f"[coches_net] tarjetas encontradas en el HTML: {len(cards)}")
    for card in cards:
        link_el = card.select_one("a[href]")
        if not link_el:
            continue
        href = link_el.get("href")
        if href and href.startswith("/"):
            href = "https://www.coches.net" + href

        title_el = card.select_one("h2, [class*='title']")
        price_el = card.select_one("[class*='rice']")

        results.append({
            "url": href,
            "title": title_el.get_text(strip=True) if title_el else None,
            "price": parse_price(price_el.get_text()) if price_el else None,
        })

    return results
