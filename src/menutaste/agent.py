from __future__ import annotations

from typing import Dict, List

from .llm_client import generate_ai_reasoning
from .models import AgentReport, NutritionEstimate, ProductInput, RiskAssessment, ScoreCard
from .nutrition_db import NUTRITION_HINTS
from .scoring import calculate_scores, detect_allergens, estimate_nutrition


def wants_italian(product: ProductInput) -> bool:
    return product.language.lower().startswith("italian")


def build_ingredient_notes(ingredients: List[str], italian: bool = False) -> Dict[str, str]:
    notes = {}
    default_note = (
        "Segnale specifico non trovato; controlla quantità, origine e metodo di preparazione."
        if italian
        else "No specific signal found; review quantity, sourcing, and preparation method."
    )
    note_translations = {
        "strong protein source": "forte fonte di proteine",
        "high protein but can raise fat level": "alto contenuto proteico ma può aumentare il livello di grassi",
        "protein-rich and common allergen": "ricco di proteine e allergene comune",
        "dairy allergen risk": "rischio allergene legato ai latticini",
        "dairy-based ingredient": "ingrediente a base di latticini",
        "dairy and salt risk": "rischio legato a latticini e sale",
        "plant protein and fiber": "proteine vegetali e fibre",
        "main carbohydrate source": "principale fonte di carboidrati",
        "gluten source": "fonte di glutine",
        "starchy carbohydrate": "carboidrato amidaceo",
        "healthy fat source": "fonte di grassi salutari",
        "high saturated fat and dairy": "alto contenuto di grassi saturi e latticini",
        "raises sugar risk": "aumenta il rischio zuccheri",
        "natural sugar but still sugar risk": "zucchero naturale ma comunque rischio zuccheri",
        "raises sodium risk": "aumenta il rischio sodio",
        "strong micronutrient signal": "forte segnale di micronutrienti",
        "freshness and vitamin signal": "freschezza e segnale vitaminico",
        "fruit sugar and potassium": "zuccheri della frutta e potassio",
        "healthy fat and premium positioning": "grassi salutari e posizionamento premium",
        "allergen and healthy fat": "allergene e grassi salutari",
        "major allergen": "allergene principale",
        "shellfish allergen": "allergene crostacei",
        "protein and omega-fat signal": "proteine e segnale di grassi omega",
    }

    for ingredient in ingredients:
        note = default_note
        for key, data in NUTRITION_HINTS.items():
            if key in ingredient:
                raw_note = data.get("note", default_note)
                note = note_translations.get(raw_note, raw_note) if italian else raw_note
                break
        notes[ingredient] = note
    return notes


def assess_risks(product: ProductInput) -> RiskAssessment:
    italian = wants_italian(product)
    allergens = detect_allergens(product.ingredients)
    joined = " ".join(product.ingredients).lower()
    focus = product.dietary_focus.lower()

    dietary_conflicts = []
    if focus == "vegan" and any(x in joined for x in ["milk", "cheese", "egg", "chicken", "beef", "fish", "shrimp"]):
        dietary_conflicts.append(
            "L'obiettivo vegano è in conflitto con ingredienti di origine animale."
            if italian else "The vegan focus conflicts with animal-based ingredients."
        )
    if focus == "vegetarian" and any(x in joined for x in ["chicken", "beef", "fish", "shrimp"]):
        dietary_conflicts.append(
            "L'obiettivo vegetariano è in conflitto con carne o pesce."
            if italian else "The vegetarian focus conflicts with meat or seafood ingredients."
        )
    if focus == "gluten-free" and any(x in joined for x in ["wheat", "bread", "pasta"]):
        dietary_conflicts.append(
            "L'obiettivo senza glutine è in conflitto con ingredienti che contengono glutine."
            if italian else "The gluten-free focus conflicts with gluten-containing ingredients."
        )
    if focus == "dairy-free" and any(x in joined for x in ["milk", "cheese", "yogurt", "butter"]):
        dietary_conflicts.append(
            "L'obiettivo senza latticini è in conflitto con ingredienti lattiero-caseari."
            if italian else "The dairy-free focus conflicts with dairy ingredients."
        )

    quality_risks = []
    if "sugar" in joined or "honey" in joined:
        quality_risks.append(
            "Il livello di zuccheri potrebbe richiedere controllo in base alla porzione."
            if italian else "Sugar level may need control depending on portion size."
        )
    if "salt" in joined or "cheese" in joined:
        quality_risks.append(
            "Il livello di sodio potrebbe richiedere controllo per un posizionamento orientato al benessere."
            if italian else "Sodium level may need control for health-focused positioning."
        )
    if not quality_risks:
        quality_risks.append(
            "Nessun rischio di qualità importante rilevato dagli ingredienti forniti."
            if italian else "No major quality risk detected from the provided ingredients."
        )

    operational_risks = []
    if product.preparation_complexity == "High":
        operational_risks.append(
            "L'alta complessità di preparazione può rallentare il servizio e aumentare le esigenze di formazione del personale."
            if italian else "High preparation complexity can slow service and increase staff training needs."
        )
    if len(product.ingredients) > 10:
        operational_risks.append(
            "Una lista ingredienti lunga può aumentare la complessità di acquisto e gestione inventario."
            if italian else "Large ingredient list can increase sourcing and inventory complexity."
        )
    if not operational_risks:
        operational_risks.append(
            "Il rischio operativo sembra gestibile per un test MVP."
            if italian else "Operational risk appears manageable for an MVP test."
        )

    return RiskAssessment(
        allergen_risks=allergens or (["Nessun allergene comune rilevato dalla lista ingredienti."] if italian else ["No common allergen detected from the ingredient list."]),
        dietary_conflicts=dietary_conflicts or (["Nessun conflitto dietetico diretto rilevato."] if italian else ["No direct dietary conflict detected."]),
        quality_risks=quality_risks,
        operational_risks=operational_risks,
    )


def create_positioning(product: ProductInput, score: int) -> str:
    italian = wants_italian(product)
    if score >= 80:
        strength = "premium e orientata al benessere" if italian else "premium and health-aware"
    elif score >= 65:
        strength = "pratica e pronta per un test di mercato" if italian else "practical and market-test ready"
    else:
        strength = "in fase iniziale e da perfezionare" if italian else "early-stage and needs refinement"

    if italian:
        return (
            f"{product.product_name} può essere posizionato come un'offerta {strength} per "
            f"{product.customer_segment.lower()} a {product.location}. Il messaggio dovrebbe collegare gusto, "
            "trasparenza degli ingredienti e valore dietetico chiaro."
        )
    return (
        f"{product.product_name} can be positioned as a {strength} offer for "
        f"{product.customer_segment.lower()} in {product.location}. The message should connect taste, "
        "ingredient transparency, and clear dietary value."
    )


def generate_recommendations(product: ProductInput, nutrition: NutritionEstimate, risks: RiskAssessment, scores: ScoreCard) -> List[str]:
    italian = wants_italian(product)
    recs = []
    if nutrition.protein_level == "Low":
        recs.append("Aggiungi una fonte proteica più forte, come legumi, yogurt, uova, pesce, pollo, tofu o frutta secca, in base al concept." if italian else "Add a stronger protein source such as legumes, yogurt, eggs, fish, chicken, tofu, or nuts depending on the concept.")
    if nutrition.vitamin_mineral_signal == "Low":
        recs.append("Aggiungi verdure colorate, frutta, erbe o contorni fermentati per migliorare il segnale di micronutrienti." if italian else "Add colorful vegetables, fruit, herbs, or fermented sides to improve the micronutrient signal.")
    if nutrition.fiber_signal == "Low":
        recs.append("Aggiungi cereali integrali, fagioli, lenticchie, ceci, verdure o semi per migliorare le fibre." if italian else "Add whole grains, beans, lentils, chickpeas, vegetables, or seeds to improve fiber.")
    if nutrition.sugar_risk == "High":
        recs.append("Riduci gli zuccheri aggiunti o offri una versione a basso contenuto di zuccheri per clienti attenti al benessere." if italian else "Reduce added sugar or offer a low-sugar version for health-focused customers.")
    if nutrition.salt_risk == "High":
        recs.append("Controlla gli ingredienti ricchi di sale e comunica una preparazione attenta al sodio quando rilevante." if italian else "Control salt-heavy ingredients and mention sodium-conscious preparation where relevant.")
    if risks.allergen_risks and not any(x.startswith("No common") or x.startswith("Nessun allergene") for x in risks.allergen_risks):
        recs.append("Aggiungi etichette allergeni chiare sul menu e forma il personale per rispondere alle domande sugli allergeni." if italian else "Add clear allergen labels on the menu and train staff to answer allergen questions.")
    if scores.market_fit_score < 70:
        recs.append("Testa una porzione più piccola o un prezzo d'ingresso più basso per validare la domanda prima di scalare." if italian else "Test a smaller portion or lower entry price to validate demand before scaling.")
    if product.preparation_complexity == "High":
        recs.append("Crea un flusso di preparazione semplificato e pre-prepara componenti sicuri per ridurre i ritardi nel servizio." if italian else "Create a simplified prep workflow and pre-batch safe components to reduce service delays.")

    recs.append("Esegui un piccolo test di degustazione e raccogli valutazioni su gusto, accettazione del prezzo e intenzione di riacquisto." if italian else "Run a small customer tasting test and collect ratings for taste, price acceptance, and repeat purchase intent.")
    return recs


def build_launch_checklist(product: ProductInput) -> List[str]:
    if wants_italian(product):
        return [
            "Finalizzare ricetta e dimensione della porzione.",
            "Calcolare costo unitario e margine lordo.",
            "Creare etichette per allergeni e preferenze dietetiche.",
            "Preparare 3 domande per il test con i clienti.",
            "Eseguire un test di degustazione con almeno 10 clienti target.",
            "Raccogliere feedback su gusto, prezzo e chiarezza della descrizione nel menu.",
            "Adattare ricetta e prezzo in base al feedback.",
            "Preparare foto di lancio, breve caption e descrizione menu.",
            f"Testare l'offerta a {product.location} con una finestra di lancio limitata.",
        ]
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
    italian = wants_italian(product)
    nutrition = NutritionEstimate(**estimate_nutrition(product.ingredients))
    risks = assess_risks(product)
    scores = ScoreCard(**calculate_scores(
        ingredients=product.ingredients,
        target_price_eur=product.target_price_eur,
        dietary_focus=product.dietary_focus,
        complexity=product.preparation_complexity,
        business_type=product.business_type,
        customer_segment=product.customer_segment,
        location=product.location,
        description=product.description,
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
        f"Complexity: {product.preparation_complexity}\n"
        f"Output language: {product.language}"
    )

    ai_reasoning = generate_ai_reasoning(product_summary, deterministic_summary, product.language)
    positioning = create_positioning(product, scores.overall_score)
    recommendations = generate_recommendations(product, nutrition, risks, scores)

    if italian:
        executive_summary = (
            f"MenuTaste ha analizzato {product.product_name} per un concept {product.business_type.lower()} a "
            f"{product.location}. Il prodotto ha ricevuto un punteggio complessivo di {scores.overall_score}/100. "
            "Il prossimo passo è validare gusto, prezzo, allergeni e disponibilità all'acquisto con un piccolo pilot."
        )
    else:
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
        ingredient_notes=build_ingredient_notes(product.ingredients, italian),
    )
