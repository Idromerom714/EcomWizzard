"""Interfaz Streamlit para descubrir y preparar productos ecommerce."""

import os
from typing import Any

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Ecommerce Tool", page_icon="🛒", layout="wide", initial_sidebar_state="collapsed")
API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

st.markdown("""<style>
:root { --accent:#ff4b4b; }
.block-container { max-width: 1180px; padding-top: 2rem; }
.hero { padding: 1.2rem 0 1.7rem; border-bottom: 1px solid rgba(128,128,128,.2); margin-bottom: 1.5rem; }
.hero h1 { font-size: clamp(2rem, 5vw, 4rem); letter-spacing: 0; margin: 0; }
.metric { padding: 1rem; border: 1px solid rgba(128,128,128,.25); border-radius: 8px; }
@media (max-width: 700px) { .block-container { padding: 1rem; } }
</style>""", unsafe_allow_html=True)

for key, default in {"step": "idle", "product": None, "sentiment": None, "history": [], "candidates": [], "selected_index": 0, "shopify_store_url": "", "shopify_access_token": ""}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def api_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{API_URL}{path}", json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


with st.sidebar:
    st.markdown("## Shopify")
    st.caption("Tus credenciales solo se usan durante esta sesión.")
    st.session_state.shopify_store_url = st.text_input("URL de la tienda", value=st.session_state.shopify_store_url, placeholder="https://mi-tienda.myshopify.com")
    st.session_state.shopify_access_token = st.text_input("Admin API access token", value=st.session_state.shopify_access_token, type="password", placeholder="shpat_...")
    st.divider()
    st.markdown("## Historial")
    if not st.session_state.history:
        st.caption("Aun no hay productos analizados.")
    for item in reversed(st.session_state.history[-8:]):
        st.write(f"**{item['name']}**  \n${item['price']:.2f}")

st.markdown('<div class="hero"><h1>EcomWizzard 🛒</h1><p>Descubre productos, entiende a tus clientes y prepara tu siguiente lanzamiento.</p></div>', unsafe_allow_html=True)
mode = st.radio("Origen del análisis", ["Producto individual", "Categoría / Best sellers"], horizontal=True)
url = st.text_input("URL de la página", placeholder="https://ejemplo.com/categoria o https://ejemplo.com/producto", label_visibility="visible")

if st.button("🔍 Buscar productos" if mode == "Categoría / Best sellers" else "🔍 Analizar producto", type="primary", use_container_width=False):
    if not url.strip().startswith(("http://", "https://")):
        st.error("Introduce una URL valida que empiece por http:// o https://")
    else:
        try:
            progress = st.progress(0, text="🔍 Scraping...")
            st.session_state.step = "scraping"
            if mode == "Categoría / Best sellers":
                scraped = api_post("/api/scrape-category", {"url": url.strip()})
                if not scraped.get("success"):
                    raise RuntimeError(scraped.get("error", "No se pudo analizar la categoría"))
                st.session_state.candidates = scraped.get("products", [])
                st.session_state.product = None
                st.session_state.sentiment = None
                st.session_state.step = "choose"
                progress.progress(100, text="Selecciona un producto para continuar")
                st.rerun()
            scraped = api_post("/api/scrape", {"url": url.strip()})
            if not scraped.get("success"):
                raise RuntimeError(scraped.get("error", "No se pudo analizar el producto"))
            st.session_state.product = scraped["data"]
            progress.progress(45, text="📊 Analizando sentimiento...")
            st.session_state.sentiment = api_post("/api/analyze-sentiment", {"reviews": st.session_state.product.get("reviews", [])})
            progress.progress(75, text="👀 Generando preview...")
            st.session_state.step = "ready"
            progress.progress(100, text="Producto listo para revisar")
            product = st.session_state.product
            if not any(item["product_url"] == product["product_url"] for item in st.session_state.history):
                st.session_state.history.append(product)
            st.rerun()
        except (requests.RequestException, RuntimeError) as exc:
            st.error(f"No se pudo completar el analisis: {exc}")

if st.session_state.candidates:
    st.subheader("Elige un producto para continuar")
    st.caption("Se han encontrado hasta cinco productos. Solo el seleccionado se analizará y preparará para Shopify.")
    labels = [f"{item['name']} · {item['price']:.2f} {item.get('currency', 'USD')}" for item in st.session_state.candidates]
    selected = st.radio("Productos encontrados", labels, index=st.session_state.selected_index, label_visibility="collapsed")
    st.session_state.selected_index = labels.index(selected)
    preview_cols = st.columns(min(5, len(st.session_state.candidates)))
    for column, item in zip(preview_cols, st.session_state.candidates):
        with column:
            st.image(item["image_url"], use_column_width=True)
            st.caption(item["name"])
    if st.button("Continuar con este producto", type="primary"):
        try:
            product = st.session_state.candidates[st.session_state.selected_index]
            st.session_state.product = product
            st.session_state.sentiment = api_post("/api/analyze-sentiment", {"reviews": product.get("reviews", [])})
            st.session_state.candidates = []
            st.session_state.step = "ready"
            if not any(item["product_url"] == product["product_url"] for item in st.session_state.history):
                st.session_state.history.append(product)
            st.rerun()
        except requests.RequestException as exc:
            st.error(f"No se pudo analizar el producto seleccionado: {exc}")

product = st.session_state.product
sentiment = st.session_state.sentiment
if product and sentiment:
    left, right = st.columns([1.3, 1])
    with left:
        st.subheader(product["name"])
        st.image(product["image_url"], use_column_width=True)
        st.markdown(f"### {product['price']:.2f} {product.get('currency', 'USD')}")
        st.write(product["description"])
        for feature in product.get("features", []):
            st.markdown(f"- {feature}")
    with right:
        st.subheader("Lectura de opiniones")
        colors = {"positive": "#20a464", "negative": "#d64545", "neutral": "#ca8a04"}
        st.markdown(f'<div class="metric"><strong style="color:{colors.get(sentiment["sentiment"], "#666")}">{sentiment["sentiment"].upper()}</strong><br><h2>{sentiment["score"]:.0%}</h2>{sentiment["summary"]}<br>Confianza: {sentiment["confidence"]:.0%}</div>', unsafe_allow_html=True)
        st.progress(sentiment["score"], text="Score de sentimiento")
        st.subheader("Preview Shopify")
        st.info("El preview y la publicación usarán la tienda indicada en la barra lateral.")
        handle = product["name"].lower().replace(" ", "-")[:60]
        preview_url = f"{st.session_state.shopify_store_url.rstrip('/') or 'https://tienda.myshopify.com'}/products/{handle}?pb=0"
        st.link_button("👀 Abrir preview", preview_url)
        if st.button("🚀 Crear en Shopify", type="primary"):
            st.session_state.confirm_create = True
        if st.session_state.get("confirm_create"):
            st.warning("El producto se creara como DRAFT en Shopify.")
            if st.button("Confirmar creacion"):
                try:
                    if not st.session_state.shopify_store_url or not st.session_state.shopify_access_token:
                        st.error("Completa la URL y el access token de Shopify en la barra lateral.")
                        st.stop()
                    created = api_post("/api/create-product", {"product_data": product, "sentiment": sentiment, "store_url": st.session_state.shopify_store_url, "access_token": st.session_state.shopify_access_token, "confirm": True})
                    st.success(f"Producto creado: {created.get('url', created.get('id'))}")
                    st.session_state.confirm_create = False
                except requests.RequestException as exc:
                    st.error(f"Shopify no esta disponible: {exc}")

    reviews = product.get("reviews", [])
    if reviews:
        st.subheader("Comentarios detectados")
        st.dataframe(pd.DataFrame({"Comentario": reviews}), use_container_width=True, hide_index=True)
else:
    st.info("Pega una URL de producto para comenzar.")
