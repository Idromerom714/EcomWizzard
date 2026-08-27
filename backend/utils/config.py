"""Configuracion centralizada y segura para el backend."""

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Config:
    """Lee configuracion desde variables de entorno.

    Las claves son opcionales para permitir ejecutar la interfaz en modo demo.
    Las operaciones que necesitan un proveedor externo validan su clave al usarse.
    """

    scrapegraph_api_key: str = os.getenv("SCRAPEGRAPH_API_KEY", "")
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    shopify_store_url: str = os.getenv("SHOPIFY_STORE_URL", "")
    shopify_access_token: str = os.getenv("SHOPIFY_ACCESS_TOKEN", "")

    def validate(self, require_integrations: bool = False) -> list[str]:
        """Devuelve faltantes y, opcionalmente, falla si faltan integraciones."""
        required = {
            "SCRAPEGRAPH_API_KEY": self.scrapegraph_api_key,
            "OPENROUTER_API_KEY": self.openrouter_api_key,
            "SHOPIFY_STORE_URL": self.shopify_store_url,
            "SHOPIFY_ACCESS_TOKEN": self.shopify_access_token,
        }
        missing = [name for name, value in required.items() if not value]
        if missing and require_integrations:
            raise RuntimeError("Faltan variables de entorno: " + ", ".join(missing))
        if missing:
            logger.warning("Integraciones no configuradas: %s", ", ".join(missing))
        return missing


settings = Config()
settings.validate()
