"""
Cliente genérico para ejecutar "Actors" de Apify de forma síncrona y
recuperar los resultados (dataset items).

Documentación del endpoint usado:
https://docs.apify.com/api/v2#/reference/actors/run-actor-synchronously-and-get-dataset-items
"""
import requests

APIFY_BASE = "https://api.apify.com/v2"


def run_actor_sync(token: str, actor_id: str, input_data: dict, timeout: int = 320):
    """
    Ejecuta un Actor de Apify y espera a que termine, devolviendo directamente
    la lista de resultados (dataset items).

    actor_id: formato "usuario/nombre-del-actor" (se convierte automáticamente
    al formato que exige la URL de la API, con '~' en vez de '/').
    """
    actor_path = actor_id.replace("/", "~")
    url = f"{APIFY_BASE}/acts/{actor_path}/run-sync-get-dataset-items"

    resp = requests.post(
        url,
        # "timeout" aquí le dice a Apify cuánto puede tardar el Actor en el lado del servidor;
        # el "timeout" del propio requests.post (más abajo) es cuánto esperamos nosotros la respuesta.
        params={"token": token, "timeout": 280},
        json=input_data,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()  # lista de items (dicts)
