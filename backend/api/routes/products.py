"""Endpoints de productos y sentimiento."""

from fastapi import APIRouter, HTTPException

from backend.agents.scraper_agent import scraper_agent
from backend.agents.sentiment_agent import sentiment_agent
from backend.models.schemas import CategoryScrapeResponse, ProductData, ReviewsRequest, ScrapeRequest, ScrapeResponse, SentimentResult
from backend.utils.validators import validate_url

router = APIRouter()


@router.post("/scrape", response_model=ScrapeResponse)
def scrape(request: ScrapeRequest) -> ScrapeResponse:
    """Analiza una URL de producto."""
    try:
        data = ProductData.model_validate(scraper_agent.run(validate_url(str(request.url))))
        return ScrapeResponse(success=True, data=data)
    except Exception as exc:
        return ScrapeResponse(success=False, error=str(exc))


@router.post("/scrape-category", response_model=CategoryScrapeResponse)
def scrape_category_page(request: ScrapeRequest) -> CategoryScrapeResponse:
    """Analiza una categoria o pagina de best sellers y devuelve hasta cinco productos."""
    try:
        products = [ProductData.model_validate(item) for item in scraper_agent.run_category(validate_url(str(request.url)))]
        return CategoryScrapeResponse(success=True, products=products)
    except Exception as exc:
        return CategoryScrapeResponse(success=False, error=str(exc))


@router.post("/analyze-sentiment", response_model=SentimentResult)
def analyze_sentiment(request: ReviewsRequest) -> SentimentResult:
    return sentiment_agent.run(request.reviews)
