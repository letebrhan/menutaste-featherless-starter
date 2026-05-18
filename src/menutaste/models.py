from __future__ import annotations

from typing import Dict, List
from pydantic import BaseModel, Field


class ProductInput(BaseModel):
    product_name: str = Field(..., min_length=2)
    description: str = Field(..., min_length=5)
    ingredients: List[str] = Field(..., min_length=1)
    business_type: str
    location: str = Field(..., min_length=2)
    customer_segment: str
    dietary_focus: str
    target_price_eur: float = Field(..., gt=0)
    preparation_complexity: str = "Medium"
    language: str = "English"


class NutritionEstimate(BaseModel):
    protein_level: str
    carbohydrate_level: str
    fat_level: str
    vitamin_mineral_signal: str
    fiber_signal: str
    sugar_risk: str
    salt_risk: str


class RiskAssessment(BaseModel):
    allergen_risks: List[str]
    dietary_conflicts: List[str]
    quality_risks: List[str]
    operational_risks: List[str]


class ScoreCard(BaseModel):
    nutrition_score: int
    quality_score: int
    market_fit_score: int
    operational_score: int
    overall_score: int


class AgentReport(BaseModel):
    product: ProductInput
    nutrition: NutritionEstimate
    risks: RiskAssessment
    scores: ScoreCard
    ai_reasoning: str
    positioning: str
    recommendations: List[str]
    launch_checklist: List[str]
    executive_summary: str
    ingredient_notes: Dict[str, str]
