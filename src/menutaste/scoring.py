from __future__ import annotations

from collections import Counter
from typing import Dict, List

from .nutrition_db import ALLERGEN_KEYWORDS, NUTRITION_HINTS


def classify_level(score: int) -> str:
    if score >= 4:
        return "High"
    if score >= 2:
        return "Medium"
    return "Low"


def detect_allergens(ingredients: List[str]) -> List[str]:
    found = set()
    for ingredient in ingredients:
        for keyword, allergen in ALLERGEN_KEYWORDS.items():
            if keyword in ingredient:
                found.add(allergen)
    return sorted(found)


def estimate_nutrition(ingredients: List[str]) -> Dict[str, str]:
    counter = Counter()
    for ingredient in ingredients:
        for key, data in NUTRITION_HINTS.items():
            if key in ingredient:
                for signal in ["protein", "carb", "fat", "vitamin", "fiber", "sugar", "salt"]:
                    value = data.get(signal)
                    if value == "high":
                        counter[signal] += 2
                    elif value == "medium":
                        counter[signal] += 1

    return {
        "protein_level": classify_level(counter["protein"]),
        "carbohydrate_level": classify_level(counter["carb"]),
        "fat_level": classify_level(counter["fat"]),
        "vitamin_mineral_signal": classify_level(counter["vitamin"]),
        "fiber_signal": classify_level(counter["fiber"]),
        "sugar_risk": classify_level(counter["sugar"]),
        "salt_risk": classify_level(counter["salt"]),
    }


def calculate_scores(
    ingredients: List[str],
    target_price_eur: float,
    dietary_focus: str,
    complexity: str,
    business_type: str = "",
    customer_segment: str = "",
    location: str = "",
    description: str = "",
) -> Dict[str, int]:
    nutrition = estimate_nutrition(ingredients)
    allergens = detect_allergens(ingredients)

    business = business_type.lower()
    customer = customer_segment.lower()
    place = location.lower()
    desc = description.lower()
    joined_ingredients = " ".join(ingredients).lower()

    nutrition_score = 60
    if nutrition["protein_level"] == "High":
        nutrition_score += 12
    if nutrition["fiber_signal"] in {"Medium", "High"}:
        nutrition_score += 8
    if nutrition["vitamin_mineral_signal"] in {"Medium", "High"}:
        nutrition_score += 8
    if dietary_focus == "High protein" and nutrition["protein_level"] == "High":
        nutrition_score += 5
    if dietary_focus == "Low sugar" and nutrition["sugar_risk"] == "Low":
        nutrition_score += 5
    if nutrition["sugar_risk"] == "High":
        nutrition_score -= 12
    if nutrition["salt_risk"] == "High":
        nutrition_score -= 8
    if dietary_focus == "Low sugar" and any(x in joined_ingredients for x in ["sugar", "honey"]):
        nutrition_score -= 8

    quality_score = 70
    if len(ingredients) >= 4:
        quality_score += 8
    if len(ingredients) > 10:
        quality_score -= 4
    if nutrition["vitamin_mineral_signal"] == "High":
        quality_score += 8
    if any(word in desc for word in ["fresh", "premium", "artisan", "seasonal", "local"]):
        quality_score += 4
    if nutrition["fat_level"] == "High" and nutrition["sugar_risk"] == "High":
        quality_score -= 10
    if len(allergens) >= 3:
        quality_score -= 5

    market_fit_score = 65
    if dietary_focus != "None":
        market_fit_score += 10
    if target_price_eur <= 8:
        market_fit_score += 6
    elif target_price_eur >= 18:
        market_fit_score -= 5

    if "milan" in place or "italy" in place:
        market_fit_score += 3
    if business in {"cafe", "bakery", "juice or drink bar"} and target_price_eur <= 9:
        market_fit_score += 4
    if "office" in customer and target_price_eur <= 10:
        market_fit_score += 4
    if "student" in customer and target_price_eur > 8:
        market_fit_score -= 5
    if "fitness" in customer and dietary_focus in {"High protein", "Low sugar", "Vegan"}:
        market_fit_score += 5
    if "premium" in customer and target_price_eur >= 5:
        market_fit_score += 3
    if any(word in desc for word in ["ready-to-go", "light", "premium", "healthy", "breakfast", "protein"]):
        market_fit_score += 3

    operational_score = 80
    if complexity == "High":
        operational_score -= 15
    elif complexity == "Low":
        operational_score += 5
    if business in {"Food truck", "Juice or drink bar"} and complexity == "High":
        operational_score -= 5
    if business in {"Cafe", "Bakery"} and complexity == "Low":
        operational_score += 3
    if len(ingredients) > 8:
        operational_score -= 5
    if len(allergens) >= 3:
        operational_score -= 10

    scores = {
        "nutrition_score": max(0, min(100, nutrition_score)),
        "quality_score": max(0, min(100, quality_score)),
        "market_fit_score": max(0, min(100, market_fit_score)),
        "operational_score": max(0, min(100, operational_score)),
    }
    scores["overall_score"] = round(sum(scores.values()) / 4)
    return scores
