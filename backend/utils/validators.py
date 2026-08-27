"""Validaciones de entradas externas."""

from urllib.parse import urlparse


def validate_url(value: str) -> str:
    """Valida que una URL sea HTTP(S) y devuelve su valor limpio."""
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Introduce una URL valida que empiece por http:// o https://")
    return value.strip()
