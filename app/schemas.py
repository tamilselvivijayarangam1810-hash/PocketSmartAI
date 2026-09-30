from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class LoginRequest(RegisterRequest):
    pass


class RoomItem(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    quantity: int = Field(ge=1, le=50)


class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    rooms: list[str] = Field(min_length=1, max_length=10)
    items: list[RoomItem] = Field(min_length=1, max_length=30)
    style: str = Field(default="modern", max_length=80)
    city: str = Field(default="Chennai", max_length=80)


class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    guests: int = Field(ge=1, le=5000)
    event_type: str = Field(min_length=2, max_length=80)
    venue: str = Field(default="home", max_length=120)
    city: str = Field(default="Chennai", max_length=80)
    preferences: str = Field(default="", max_length=1000)


class JewelryRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    occasion: str = Field(min_length=2, max_length=80)
    style: str = Field(default="elegant", max_length=80)
    outfit_color: Optional[str] = Field(default=None, max_length=80)
    preferences: str = Field(default="", max_length=1000)


class RecommendationItem(BaseModel):
    name: str
    category: str
    platform: str
    estimated_price: float = Field(ge=0)
    quantity: int = Field(default=1, ge=1)
    reason: str
    search_url: str


class BudgetAllocation(BaseModel):
    category: str
    amount: float = Field(ge=0)


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str
    summary: str
    total_estimated_cost: float
    budget: float
    budget_remaining: float
    allocations: list[BudgetAllocation]
    recommendations: list[RecommendationItem]
    notes: list[str] = []
    source: Literal["gemini", "fallback"]
