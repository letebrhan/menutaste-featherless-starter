from __future__ import annotations

from typing import Dict, List

from .llm_client import generate_ai_reasoning
from .models import AgentReport, NutritionEstimate, ProductInput, RiskAssessment, ScoreCard
from .nutrition_db import NUTRITION_HINTS
from .scoring import calculate_scores, detect_allergens, estimate_nutrition


def build_ingredient_notes(ingredients: List[str]) -> Dict[str, str]:
    notes = {}
    for ingredient in ingredients:
        note = "No specific signal found; review quantity, sourcing, and preparation method."
        for key, data in NUTRITION_HINTS.items():
            if key in ingredient:
                note = data.get("note", note)
                break
        notes[ingredient] = note
    return notes


def assess_risks(product: ProductInput) -> RiskAssessment:
    allergens = detect_allergens(product.ingredients)
    joined = " ".join(product.ingredients).lower()
    focus = product.dietary_focus.lower()

    dietary_conflicts = []
    if focus == "vegan" and any(x in joined for x in ["milk", "cheese", "egg", "chicken", "beef", "fish", "shrimp"]):
        dietary_conflicts.append("The vegan focus conflicts with animal-based ingredients.")
    if focus == "vegetarian" and any(x in joined for x in ["chicken", "beef", "fish", "shrimp"]):
        dietary_conflicts.append("The vegetarian focus conflicts with meat or seafood ingredients.")
    if focus == "gluten-free" and any(x in joined for x in ["wheat", "bread", "pasta"]):
        dietary_conflicts.append("The gluten-free focus conflicts with gluten-containing ingredients.")
    if focus == "dairy-free" and any(x in joined for x in ["milk", "cheese", "yogurt", "butter"]):
        dietary_conflicts.append("The dairy-free focus conflicts with dairy ingredients.")

    quality_risks = []
    if "sugar" in joined or "honey" in joined:
        quality_risks.append("Sugar level may need control depending on portion size.")
    if "salt" in joined or "cheese" in joined:
        quality_risks.append("Sodium level may need control for health-focused positioning.")
    if not quality_risks:
        quality_risks.append("No major quality risk detected from the provided ingredients.")

    operational_risks = []
    if product.preparation_complexity == "High":
        operational_risks.append("High preparation complexity can slow service and increase staff training needs.")
    if len(product.ingredients) > 10:
        operational_risks.append("Large ingredient list can increase sourcing and inventory complexity.")
    if not operational_risks:
        operational_risks.append("Operational risk appears manageable for an MVP test.")

    return RiskAssessment(
        allergen_risks=allergens or ["No common allergen detected from the ingredient list."],
        dietary_conflicts=dietary_conflicts or ["No direct dietary conflict detected."],
        quality_risks=quality_risks,
        operational_risks=operational_risks,
    )


def create_positioning(product: ProductInput, score: int) -> str:
    if score >= 80:
        strength = "premium and health-aware"
    elif score >= 65:
        strength = "practical and market-test ready"
    else:
        strength = "early-stage and needs refinement"

    return (
        f"{product.product_name} can be positioned as a {strength} offer for "
        f"{product.customer_segment.lower()} in {product.location}. The message should connect taste, "
        "ingredient transparency, and clear dietary value."
    )


def generate_recommendations(product: ProductInput, nutrition: NutritionEstimate, risks: RiskAssessment, scores: ScoreCard) -> List[str]:
    recs = []
    if nutrition.protein_level == "Low":
        recs.append("Add a stronger protein source such as legumes, yogurt, eggs, fish, chicken, tofu, or nuts depending on the concept.")
    if nutrition.vitamin_mineral_signal == "Low":
        recs.append("Add colorful vegetables, fruit, herbs, or fermented sides to improve the micronutrient signal.")
    if nutrition.fiber_signal == "Low":
        recs.append("Add whole grains, beans, lentils, chickpeas, vegetables, or seeds to improve fiber.")
    if nutrition.sugar_risk == "High":
        recs.append("Reduce added sugar or offer a low-sugar version for health-focused customers.")
    if nutrition.salt_risk == "High":
        recs.append("Control salt-heavy ingredients and mention sodium-conscious preparation where relevant.")
    if risks.allergen_risks and "No common allergen" not in risks.allergen_risks[0]:
        recs.append("Add clear allergen labels on the menu and train staff to answer allergen questions.")
    if scores.market_fit_score < 70:
        recs.append("Test a smaller portion or lower entry price to validate demand before scaling.")
    if product.preparation_complexity == "High":
        recs.append("Create a simplified prep workflow and pre-batch safe components to reduce service delays.")

    recs.append("Run a small customer tasting test and collect ratings for taste, price acceptance, and repeat purchase intent.")
    return recs


def build_launch_checklist(product: ProductInput) -> List[str]:
    return [
        "Finalize recipe and portion size.",
        "Calculate unit cost and gross margin.",
        "Create allergen and dietary labels.",
        "Prepare 3 customer testing questions.",
        "Run tasting test with at least 10 target customers.",
        "Collect feedback on taste, price, and clarity of menu description.",
        "Adjust recipe and price based on feedback.",
        "Prepare launch photo, short caption, and menu description.",
        f"Pilot the offer in {product.location} with a limited launch window.",
    ]


def run_menutaste_agent(product: ProductInput) -> AgentReport:
    nutrition = NutritionEstimate(**estimate_nutrition(product.ingredients))
    risks = assess_risks(product)
    scores = ScoreCard(**calculate_scores(
        ingredients=product.ingredients,
        target_price_eur=product.target_price_eur,
        dietary_focus=product.dietary_focus,
        complexity=product.preparation_complexity,
    ))

    deterministic_summary = (
        f"Scores: nutrition {scores.nutrition_score}, quality {scores.quality_score}, "
        f"market fit {scores.market_fit_score}, operational {scores.operational_score}, overall {scores.overall_score}. "
        f"Nutrition: protein {nutrition.protein_level}, carbs {nutrition.carbohydrate_level}, fat {nutrition.fat_level}, "
        f"vitamins {nutrition.vitamin_mineral_signal}, fiber {nutrition.fiber_signal}, sugar risk {nutrition.sugar_risk}, "
        f"salt risk {nutrition.salt_risk}. Risks: allergens {', '.join(risks.allergen_risks)}."
    )

    product_summary = (
        f"Name: {product.product_name}\n"
        f"Description: {product.description}\n"
        f"Ingredients: {', '.join(product.ingredients)}\n"
        f"Business type: {product.business_type}\n"
        f"Location: {product.location}\n"
        f"Customer segment: {product.customer_segment}\n"
        f"Dietary focus: {product.dietary_focus}\n"
        f"Target price EUR: {product.target_price_eur}\n"
        f"Complexity: {product.preparation_complexity}"
    )

    ai_reasoning = generate_ai_reasoning(product_summary, deterministic_summary)
    positioning = create_positioning(product, scores.overall_score)
    recommendations = generate_recommendations(product, nutrition, risks, scores)

    executive_summary = (
        f"MenuTaste analyzed {product.product_name} for a {product.business_type.lower()} concept in "
        f"{product.location}. The product received an overall score of {scores.overall_score}/100. "
        "The next step is to validate taste, price, allergens, and customer willingness to buy through a small pilot."
    )

    return AgentReport(
        product=product,
        nutrition=nutrition,
        risks=risks,
        scores=scores,
        ai_reasoning=ai_reasoning,
        positioning=positioning,
        recommendations=recommendations,
        launch_checklist=build_launch_checklist(product),
        executive_summary=executive_summary,
        ingredient_notes=build_ingredient_notes(product.ingredients),
    )
