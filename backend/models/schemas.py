"""Esquemas Pydantic compartidos por API y frontend."""

from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, SecretStr


class ProductData(BaseModel):
    name: str
    price: float = Field(ge=0)
    currency: str = "USD"
    description: str
    features: List[str] = Field(default_factory=list)
    image_url: str
    product_url: str
    reviews: Optional[List[str]] = Field(default_factory=list)


class SentimentResult(BaseModel):
    sentiment: str
    score: float = Field(ge=0, le=1)
    summary: str
    confidence: float = Field(ge=0, le=1)


class ShopifyCreateRequest(BaseModel):
    product_data: ProductData
    sentiment: SentimentResult
    store_url: HttpUrl
    access_token: SecretStr
    confirm: bool = True


class ScrapeRequest(BaseModel):
    url: HttpUrl


class ReviewsRequest(BaseModel):
    reviews: List[str] = Field(default_factory=list)


class ScrapeResponse(BaseModel):
    success: bool
    data: Optional[ProductData] = None
    error: Optional[str] = None


class CategoryScrapeResponse(BaseModel):
    success: bool
    products: List[ProductData] = Field(default_factory=list)
    error: Optional[str] = None
