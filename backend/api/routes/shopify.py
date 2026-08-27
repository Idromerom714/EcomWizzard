"""Endpoints de preview y publicacion en Shopify."""

from fastapi import APIRouter, HTTPException

from backend.agents.shopify_agent import shopify_agent
from backend.models.schemas import ShopifyCreateRequest

router = APIRouter()


@router.get("/preview/{handle}")
def preview(handle: str) -> dict:
    """Devuelve URL de preview y datos publicos del producto si estan disponibles."""
    try:
        return {"preview_url": shopify_agent.get_preview_url(handle), "data": shopify_agent.get_product_json(handle)}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo obtener el preview: {exc}") from exc


@router.post("/create-product")
def create_product(request: ShopifyCreateRequest) -> dict:
    """Crea un producto en estado DRAFT despues de confirmacion explicita."""
    if not request.confirm:
        raise HTTPException(status_code=400, detail="La creacion requiere confirmacion")
    try:
        return shopify_agent.create_product(
            request.product_data,
            request.sentiment,
            str(request.store_url),
            request.access_token.get_secret_value(),
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
