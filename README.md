# EcomWizzard

Aplicacion de ecommerce/dropshipping con FastAPI y Streamlit.

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
./run.sh
```

Abre `http://localhost:8501`. El scraping y el sentimiento tienen modo demo sin claves; para usar IA con OpenRouter configura `OPENROUTER_API_KEY` y, opcionalmente, `OPENROUTER_MODEL` en `.env`.

## Despliegue

En Streamlit Community Cloud selecciona `frontend/app.py` y define `API_URL` apuntando a un backend FastAPI desplegado, por ejemplo en Render o Railway. Para Docker: `docker build -t ecomwizzard . && docker run -p 8501:8501 -p 8000:8000 ecomwizzard`.

Health check: `GET /api/health`.