"""
Scraper para Milanuncios. Basado en parseo de HTML — revisar selectores
si la web cambia (marcados como AJUSTAR SI CAMBIA LA WEB).
"""
from bs4 import BeautifulSoup
from ..utils import fetch, parse_price

SITE_NAME = "milanuncios"


def check_listing(session, url, delay):
    try:
        resp = fetch(session, url, delay=delay)
    except Exception:
        return {"active": False, "price": None, "title": None}

    soup = BeautifulSoup(resp.text, "lxml")
    title_el = soup.select_one("h1")
    title = title_el.get_text(strip=True) if title_el else None

    price_el = soup.select_one("[class*='price'], [data-testid*='price']")
    price = parse_price(price_el.get_text()) if price_el else None

    active = title is not None
    return {"active": active, "price": price, "title": title}


def run_search(session, query: str, max_price, delay: float):
    url = "https://www.milanuncios.com/segunda-mano-de-coches/"
    params = {"s": query, "pma": max_price}

    results = []
    try:
        resp = fetch(session, url, delay=delay, params=params)
    except Exception:
        return results

    soup = BeautifulSoup(resp.text, "lxml")
    cards = soup.select("article, [class*='item'], [class*='Item']")
    for card in cards:
        link_el = card.select_one("a[href]")
        if not link_el:
            continue
        href = link_el.get("href")
        if href and href.startswith("/"):
            href = "https://www.milanuncios.com" + href

        title_el = card.select_one("h2, [class*='title']")
        price_el = card.select_one("[class*='price']")

        results.append({
            "url": href,
            "title": title_el.get_text(strip=True) if title_el else None,
            "price": parse_price(price_el.get_text()) if price_el else None,
        })
    return results
