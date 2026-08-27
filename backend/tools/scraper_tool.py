"""Adaptador de scraping con ScrapeGraph y reintentos."""

import logging
import time
from typing import Any

from backend.utils.config import settings

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """Extrae un producto ecommerce de esta pagina. Devuelve JSON con name, price, currency,
description, features (lista), image_url, product_url y reviews (lista de comentarios).
Usa solo datos visibles, conserva la moneda original y devuelve price como numero."""

CATEGORY_EXTRACTION_PROMPT = """Analiza una pagina de categoria, best sellers o resultados de busqueda ecommerce.
Devuelve JSON con una lista products de hasta 5 productos, ordenados de mayor a menor relevancia.
Cada producto debe incluir name, price, currency, description breve, features, image_url,
product_url y reviews. No inventes URLs ni productos que no aparezcan en la pagina."""


def scrape_product(url: str, retries: int = 3, timeout: int = 30) -> dict[str, Any]:
    """Extrae datos con backoff exponencial; incluye fallback demo sin API key."""
    if not settings.scrapegraph_api_key:
        return {
            "name": "Producto de demostracion", "price": 29.99, "currency": "USD",
            "description": "Producto listo para revisar y publicar en tu tienda.",
            "features": ["Envio internacional", "Diseno funcional", "Valoracion verificada"],
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=900",
            "product_url": url, "reviews": ["Muy buena calidad y entrega rapida.", "Supero mis expectativas."],
        }
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            try:
                from crewai_tools import ScrapegraphScrapeTool

                tool = ScrapegraphScrapeTool(api_key=settings.scrapegraph_api_key)
                result = tool.run(url=url, prompt=EXTRACTION_PROMPT, timeout=timeout)
            except ImportError:
                from scrapegraph_py import Client

                client = Client(api_key=settings.scrapegraph_api_key)
                result = client.scrape(url=url, prompt=EXTRACTION_PROMPT, timeout=timeout)
            if isinstance(result, dict):
                return result
            return result.json() if hasattr(result, "json") else result
        except Exception as exc:  # proveedor externo: conservar el ultimo error
            last_error = exc
            logger.warning("Scrape intento %s/%s fallido: %s", attempt + 1, retries, exc)
            if attempt < retries - 1:
                time.sleep(2**attempt)
    raise RuntimeError(f"No se pudo analizar la pagina: {last_error}")


def scrape_category(url: str, retries: int = 3, timeout: int = 30) -> list[dict[str, Any]]:
    """Extrae hasta cinco productos de una categoria, con fallback para demo."""
    if not settings.scrapegraph_api_key:
        return [
            {"name": f"Producto destacado {index}", "price": round(19.99 + index * 7, 2), "currency": "USD",
             "description": "Una oportunidad de producto seleccionada para tu catalogo.",
             "features": ["Alta demanda", "Facil de enviar"],
             "image_url": f"https://images.unsplash.com/photo-{photo}?w=700",
             "product_url": f"{url.rstrip('/')}/producto-{index}", "reviews": ["Buena calidad y entrega rapida."]}
            for index, photo in enumerate([1523275335684, 1496181133206, 1542291026, 1556742049, 1526170375885], 1)
        ]
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            try:
                from crewai_tools import ScrapegraphScrapeTool
                tool = ScrapegraphScrapeTool(api_key=settings.scrapegraph_api_key)
                result = tool.run(url=url, prompt=CATEGORY_EXTRACTION_PROMPT, timeout=timeout)
            except ImportError:
                from scrapegraph_py import Client
                result = Client(api_key=settings.scrapegraph_api_key).scrape(url=url, prompt=CATEGORY_EXTRACTION_PROMPT, timeout=timeout)
            payload = result if isinstance(result, dict) else result.json()
            products = payload.get("products", payload if isinstance(payload, list) else [])
            return products[:5]
        except Exception as exc:
            last_error = exc
            logger.warning("Categoria intento %s/%s fallido: %s", attempt + 1, retries, exc)
            if attempt < retries - 1:
                time.sleep(2**attempt)
    raise RuntimeError(f"No se pudo analizar la categoria: {last_error}")
