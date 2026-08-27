"""Analisis de sentimiento con fallback local y salida estructurada."""

import re
from typing import Iterable

import requests

from backend.models.schemas import SentimentResult
from backend.utils.config import settings


class SentimentAgent:
    """Clasifica comentarios y devuelve una respuesta JSON validada."""

    positive_words = {"bueno", "buena", "excelente", "genial", "rapido", "rapida", "recomiendo", "calidad", "love", "great"}
    negative_words = {"malo", "mala", "pesimo", "pesima", "lento", "lenta", "defecto", "problema", "hate", "bad"}

    def run(self, reviews: Iterable[str]) -> SentimentResult:
        texts = list(reviews)
        if settings.openrouter_api_key and texts:
            try:
                return self._run_openrouter(texts)
            except (requests.RequestException, ValueError, KeyError, TypeError):
                pass
        return self._run_local(texts)

    def _run_openrouter(self, reviews: list[str]) -> SentimentResult:
        """Solicita JSON estructurado a OpenRouter."""
        response = requests.post(
            f"{settings.openrouter_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://ecomwizzard.app",
                "X-Title": "EcomWizzard",
            },
            json={
                "model": settings.openrouter_model,
                "messages": [{"role": "system", "content": "Analiza opiniones ecommerce y responde solo JSON con sentiment (positive/negative/neutral), score (0-1), summary y confidence (0-1)."}, {"role": "user", "content": "\n".join(reviews)}],
                "response_format": {"type": "json_object"},
            },
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        import json
        return SentimentResult.model_validate(json.loads(content))

    def _run_local(self, texts: list[str]) -> SentimentResult:
        """Calcula una señal estable sin bloquear el arranque."""
        words = re.findall(r"[a-záéíóúñ]+", " ".join(texts).lower())
        positive = sum(word in self.positive_words for word in words)
        negative = sum(word in self.negative_words for word in words)
        total = positive + negative
        if positive > negative:
            sentiment, score = "positive", min(1.0, 0.55 + positive / max(10, len(words)))
        elif negative > positive:
            sentiment, score = "negative", min(1.0, 0.55 + negative / max(10, len(words)))
        else:
            sentiment, score = "neutral", 0.5
        confidence = min(1.0, 0.55 + total / max(10, len(words))) if words else 0.35
        summary = {"positive": "Los comentarios reflejan una recepcion favorable.", "negative": "Los comentarios muestran varios puntos de friccion.", "neutral": "Los comentarios no muestran una tendencia clara."}[sentiment]
        return SentimentResult(sentiment=sentiment, score=round(score, 2), summary=summary, confidence=round(confidence, 2))


sentiment_agent = SentimentAgent()
