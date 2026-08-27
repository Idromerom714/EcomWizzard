"""Cliente minimo para preview y Admin GraphQL de Shopify."""

from typing import Any

import requests

from backend.models.schemas import ProductData, SentimentResult
from backend.utils.config import settings


class ShopifyAgent:
    """Gestiona productos Shopify mediante su API Admin GraphQL."""

    @staticmethod
    def _base_url(store_url: str) -> str:
        return store_url.rstrip("/").replace("https://", "").replace("http://", "")

    def get_preview_url(self, handle: str, store_url: str | None = None) -> str:
        configured_url = store_url or settings.shopify_store_url
        return f"https://{self._base_url(configured_url)}/products/{handle}?pb=0"

    def get_product_json(self, handle: str, store_url: str | None = None) -> dict[str, Any]:
        configured_url = store_url or settings.shopify_store_url
        response = requests.get(f"https://{self._base_url(configured_url)}/products/{handle}.js", timeout=30)
        response.raise_for_status()
        return response.json()

    def create_product(self, product_data: ProductData, sentiment: SentimentResult, store_url: str, access_token: str) -> dict[str, str]:
        if not store_url or not access_token:
            raise ValueError("Las credenciales de Shopify son obligatorias")
        query = """mutation CreateProduct($input: ProductInput!) { productCreate(input: $input) { product { id handle } userErrors { field message } } }"""
        tags = ["dropshipping", f"sentiment:{sentiment.sentiment}"]
        variables = {"input": {"title": product_data.name, "descriptionHtml": product_data.description, "status": "DRAFT", "tags": tags, "variants": [{"price": str(product_data.price)}], "images": [{"src": product_data.image_url}]}}
        endpoint = f"https://{self._base_url(store_url)}/admin/api/2024-01/graphql.json"
        response = requests.post(endpoint, json={"query": query, "variables": variables}, headers={"X-Shopify-Access-Token": access_token}, timeout=30)
        response.raise_for_status()
        payload = response.json()
        result = payload.get("data", {}).get("productCreate", {})
        if result.get("userErrors"):
            raise RuntimeError("; ".join(error["message"] for error in result["userErrors"]))
        product = result.get("product", {})
        return {"id": product["id"], "url": self.get_preview_url(product["handle"], store_url)}


shopify_agent = ShopifyAgent()
