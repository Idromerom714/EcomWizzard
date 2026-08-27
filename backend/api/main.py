"""Aplicacion FastAPI principal."""

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes import products, shopify

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="EcomWizzard API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(shopify.router, prefix="/api", tags=["shopify"])


@app.middleware("http")
async def request_logger(request: Request, call_next):
    request_id = uuid.uuid4().hex[:8]
    started = time.perf_counter()
    try:
        response = await call_next(request)
        logger.info("%s %s %s %.0fms id=%s", request.method, request.url.path, response.status_code, (time.perf_counter() - started) * 1000, request_id)
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception:
        logger.exception("Error no controlado id=%s", request_id)
        raise


@app.exception_handler(Exception)
async def handle_exception(_: Request, exc: Exception):
    logger.exception("Excepcion global: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Ha ocurrido un error interno. Intentalo de nuevo."})


@app.get("/api/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ecomwizzard-api"}
