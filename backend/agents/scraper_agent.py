"""Agente especializado en extraccion de catalogo."""

from typing import Any

from backend.tools.scraper_tool import scrape_category, scrape_product


class EcommerceScraperAgent:
    """Orquesta la herramienta de scraping y normaliza su resultado."""

    role = "Scraper Especializado en Ecommerce"

    def run(self, url: str) -> dict[str, Any]:
        """Extrae datos precisos del producto indicado."""
        return scrape_product(url)

    def run_category(self, url: str) -> list[dict[str, Any]]:
        """Extrae los cinco productos mas relevantes de una pagina de listado."""
        return scrape_category(url)


scraper_agent = EcommerceScraperAgent()
