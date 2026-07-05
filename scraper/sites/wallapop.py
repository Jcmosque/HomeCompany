def run_search(session, query: str, max_price, location: str, delay: float):
    # Parámetros confirmados observando la URL real de búsqueda en es.wallapop.com
    params = {
        "keywords": query,
        "category_id": 100,          # 100 = Coches
        "max_sale_price": max_price,
        "order_by": "most_relevance",
    }
