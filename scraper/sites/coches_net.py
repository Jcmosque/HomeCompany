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
        # 404 / redirección a portada suele indicar que el anuncio se ha retirado (vendido)
        return {"active": False, "price": None, "title": None}

    soup = BeautifulSoup(resp.text, "lxml")

    # AJUSTAR SI CAMBIA LA WEB: título del anuncio
    title_el = soup.select_one("h1")
    title = title_el.get_text(strip=True) if title_el else None

    # AJUSTAR SI CAMBIA LA WEB: precio — probamos varias posibles ubicaciones
    price = None
    price_el = soup.select_one("[class*='Price'], [data-testid*='price'], .mt-PriceRow-price")
    if price_el:
        price = parse_price(price_el.get_text())

    # Si la página ya no tiene título de anuncio, asumimos que fue retirado/vendido
    active = title is not None
    return {"active": active, "price": price, "title": title}


def run_search(session, params: dict, delay: float):
    """Ejecuta una búsqueda por criterios y devuelve lista de anuncios encontrados."""
    base = "https://www.coches.net/segunda-mano/"

    query = {}
    if params.get("marca"):
        query["MakeIds"] = params["marca"]
    if params.get("modelo"):
        query["ModelIds"] = params["modelo"]
    if params.get("precio_max"):
        query["MaxPrice"] = params["precio_max"]
    if params.get("provincia"):
        query["Provincies"] = params["provincia"]
    if params.get("combustible"):
        query["FuelTypeIds"] = params["combustible"]

    results = []
    try:
        resp = fetch(session, base, delay=delay, params=query)
    except Exception:
        return results

    soup = BeautifulSoup(resp.text, "lxml")

    # AJUSTAR SI CAMBIA LA WEB: tarjetas de resultados de búsqueda
    cards = soup.select("article, [class*='CardListing'], [data-ad-id]")
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
