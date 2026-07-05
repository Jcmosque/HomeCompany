"""
Orquestador principal.

Ejecuta:
  1. Comprobación de anuncios concretos guardados (tracked_urls) -> detecta
     cambios de precio y si han sido retirados (probablemente vendidos).
  2. Búsquedas guardadas (searches) -> detecta anuncios NUEVOS desde la
     última ejecución.

Guarda todo en docs/data/listings.json, que es lo que lee el panel (dashboard).
Este script está pensado para ejecutarse periódicamente vía GitHub Actions,
pero también puedes correrlo tú a mano con: python -m scraper.scraper
"""
import json
import hashlib
import os
from datetime import datetime, timezone

import yaml

from .utils import get_session
from .sites import wallapop, milanuncios, autocasion
from .sites import apify_coches_net

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "scraper", "config.yaml")
DATA_PATH = os.path.join(BASE_DIR, "docs", "data", "listings.json")

APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")

SITE_MODULES = {
    "wallapop": wallapop,
    "milanuncios": milanuncios,
    "autocasion": autocasion,
    "apify_coches_net": apify_coches_net,
}


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"listings": {}, "new_this_run": [], "last_run": None, "run_history": []}


def save_data(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def make_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def update_listing_record(data, url, label, site, result):
    lid = make_id(url)
    now = now_iso()
    record = data["listings"].get(lid)

    if record is None:
        record = {
            "id": lid,
            "url": url,
            "label": label,
            "site": site,
            "title": result.get("title"),
            "first_seen": now,
            "last_checked": now,
            "status": "active" if result.get("active") else "sold_or_removed",
            "current_price": result.get("price"),
            "price_history": [],
        }
        if result.get("price") is not None:
            record["price_history"].append({"date": now, "price": result["price"]})
        data["listings"][lid] = record
        return record, "new"

    change = None
    record["last_checked"] = now
    new_status = "active" if result.get("active") else "sold_or_removed"

    if record["status"] == "active" and new_status == "sold_or_removed":
        change = "sold_or_removed"
    record["status"] = new_status

    new_price = result.get("price")
    if new_price is not None and new_price != record.get("current_price"):
        record["price_history"].append({"date": now, "price": new_price})
        if record.get("current_price") is not None:
            change = "price_changed"
        record["current_price"] = new_price

    return record, change


def main():
    config = load_config()
    data = load_data()
    settings = config.get("settings", {})
    delay = settings.get("request_delay_seconds", 3)
    session = get_session(settings.get("user_agent", "Mozilla/5.0"))

    events = []  # cambios detectados en esta ejecución (para notificaciones/histórico)
    new_from_searches = []

    # --- 1) Anuncios concretos guardados ---
    for item in config.get("tracked_urls", []):
        url = item["url"]
        label = item.get("label", url)
        site = SITE_NAME_FROM_URL(url)
        module = SITE_MODULES.get(site)
        if not module:
            continue
        try:
            result = module.check_listing(session, url, delay)
        except Exception as e:
            print(f"AVISO: fallo comprobando '{label}' ({site}): {e}")
            continue
        record, change = update_listing_record(data, url, label, site, result)
        if change:
            events.append({"id": record["id"], "url": url, "label": label, "change": change,
                            "price": record.get("current_price"), "date": now_iso()})

    # --- 2) Búsquedas por criterios -> detectar anuncios nuevos ---
    for search in config.get("searches", []):
        site = search["site"]
        module = SITE_MODULES.get(site)
        if not module:
            continue

        try:
            if site == "apify_coches_net":
                results = module.run_search(session, search.get("params") or {}, delay, APIFY_TOKEN)
            elif site == "wallapop":
                results = module.run_search(session, search.get("query", ""), search.get("max_price"),
                                              search.get("location", "Madrid"), delay)
            elif site == "milanuncios":
                results = module.run_search(session, search.get("query", ""), search.get("max_price"), delay)
            elif site == "autocasion":
                results = module.run_search(session, search.get("params") or {}, delay)
            else:
                results = []
        except Exception as e:
            print(f"AVISO: fallo en la búsqueda '{search.get('label')}' ({site}): {e}")
            results = []

        # Blindaje: si algo devuelve None o algo no iterable, no debe tumbar todo el proceso
        if not results:
            continue

        for r in results:
            if not r.get("url"):
                continue
            lid = make_id(r["url"])
            is_new = lid not in data["listings"]
            record, _ = update_listing_record(
                data, r["url"], f"[Búsqueda: {search.get('label')}]", site,
                {"active": True, "price": r.get("price"), "title": r.get("title")}
            )
            record["from_search"] = search.get("label")
            if is_new:
                new_from_searches.append({
                    "id": lid, "url": r["url"], "title": r.get("title"),
                    "price": r.get("price"), "site": site,
                    "search_label": search.get("label"), "date": now_iso(),
                })

    data["new_this_run"] = new_from_searches
    data["last_run"] = now_iso()
    data.setdefault("run_history", []).append({
        "date": data["last_run"],
        "events": events,
        "new_count": len(new_from_searches),
    })
    # Nos quedamos solo con las últimas 200 ejecuciones para no crecer sin límite
    data["run_history"] = data["run_history"][-200:]

    save_data(data)
    print(f"OK. {len(events)} cambios detectados. {len(new_from_searches)} anuncios nuevos.")


def SITE_NAME_FROM_URL(url: str) -> str:
    if "coches.net" in url:
        return "coches_net"
    if "wallapop" in url:
        return "wallapop"
    if "milanuncios" in url:
        return "milanuncios"
    if "autocasion" in url:
        return "autocasion"
    return "desconocido"


if __name__ == "__main__":
    main()
