"""
Scraper para Autocasion. Basado en parseo de HTML — revisar selectores
si la web cambia (marcados como AJUSTAR SI CAMBIA LA WEB).
"""
from bs4 import BeautifulSoup
from ..utils import fetch, parse_price

SITE_NAME = "autocasion"


def check_listing(session, url, delay):
    try:
        resp = fetch(session, url, delay=delay)
    except Exception:
        return {"active": False, "price": None, "title": None}

    soup = BeautifulSoup(resp.text, "lxml")
    title_el = soup.select_one("h1")
    title = title_el.get_text(strip=True) if title_el else None

    price_el = soup.select_one("[class*='price'], [class*='Price']")
    price = parse_price(price_el.get_text()) if price_el else None

    active = title is not None
    return {"active": active, "price": price, "title": title}


def run_search(session, params: dict, delay: float):
    url = "https://www.autocasion.com/coches-ocasion/"
    q = {}
    if params.get("marca"):
        q["marca"] = params["marca"]
    if params.get("modelo"):
        q["modelo"] = params["modelo"]
    if params.get("precio_max"):
        q["precioHasta"] = params["precio_max"]

    results = []
    try:
        resp = fetch(session, url, delay=delay, params=q)
    except Exception:
        return results

    soup = BeautifulSoup(resp.text, "lxml")
    cards = soup.select("article, [class*='card'], [class*='Card']")
    for card in cards:
        link_el = card.select_one("a[href]")
        if not link_el:
            continue
        href = link_el.get("href")
        if href and href.startswith("/"):
            href = "https://www.autocasion.com" + href

        title_el = card.select_one("h2, [class*='title']")
        price_el = card.select_one("[class*='price']")

        results.append({
            "url": href,
            "title": title_el.get_text(strip=True) if title_el else None,
            "price": parse_price(price_el.get_text()) if price_el else None,
        })
    return results
