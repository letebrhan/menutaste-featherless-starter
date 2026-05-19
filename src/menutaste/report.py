from __future__ import annotations

from .models import AgentReport


def _is_italian(report: AgentReport) -> bool:
    return report.product.language.lower().startswith("italian")


def _level(value: str, italian: bool) -> str:
    if not italian:
        return value
    return {
        "High": "Alto",
        "Medium": "Medio",
        "Low": "Basso",
    }.get(value, value)


def report_to_markdown(report: AgentReport) -> str:
    product = report.product
    italian = _is_italian(report)

    if italian:
        labels = {
            "title": f"# Report MenuTaste: {product.product_name}",
            "executive": "## Riepilogo esecutivo",
            "reasoning": "## Ragionamento AI Featherless",
            "context": "## Contesto prodotto",
            "business_type": "Tipo di attivita",
            "location": "Localita",
            "customer": "Segmento clienti",
            "dietary": "Focus dietetico",
            "price": "Prezzo target",
            "scores": "## Punteggi",
            "nutrition_score": "Punteggio nutrizione",
            "quality_score": "Punteggio qualita",
            "market_score": "Punteggio market fit",
            "ops_score": "Punteggio operativo",
            "overall_score": "Punteggio totale",
            "nutrition": "## Stima nutrizionale",
            "protein": "Proteine",
            "carbs": "Carboidrati",
            "fat": "Grassi",
            "vitamins": "Segnale vitamine/minerali",
            "fiber": "Segnale fibre",
            "sugar": "Rischio zucchero",
            "salt": "Rischio sale",
            "risks": "## Rischi",
            "allergens": "### Allergeni",
            "conflicts": "### Conflitti dietetici",
            "quality": "### Rischi qualita",
            "operations": "### Rischi operativi",
            "positioning": "## Posizionamento",
            "ingredient_notes": "## Note sugli ingredienti",
            "recommendations": "## Raccomandazioni",
            "checklist": "## Checklist di lancio",
        }
    else:
        labels = {
            "title": f"# MenuTaste Report: {product.product_name}",
            "executive": "## Executive Summary",
            "reasoning": "## Featherless AI Reasoning",
            "context": "## Product Context",
            "business_type": "Business type",
            "location": "Location",
            "customer": "Customer segment",
            "dietary": "Dietary focus",
            "price": "Target price",
            "scores": "## Scores",
            "nutrition_score": "Nutrition score",
            "quality_score": "Quality score",
            "market_score": "Market fit score",
            "ops_score": "Operational score",
            "overall_score": "Overall score",
            "nutrition": "## Nutrition Estimate",
            "protein": "Protein",
            "carbs": "Carbohydrates",
            "fat": "Fat",
            "vitamins": "Vitamin/mineral signal",
            "fiber": "Fiber signal",
            "sugar": "Sugar risk",
            "salt": "Salt risk",
            "risks": "## Risks",
            "allergens": "### Allergens",
            "conflicts": "### Dietary Conflicts",
            "quality": "### Quality Risks",
            "operations": "### Operational Risks",
            "positioning": "## Positioning",
            "ingredient_notes": "## Ingredient Notes",
            "recommendations": "## Recommendations",
            "checklist": "## Launch Checklist",
        }

    lines = [
        labels["title"],
        "",
        labels["executive"],
        report.executive_summary,
        "",
        labels["reasoning"],
        report.ai_reasoning,
        "",
        labels["context"],
        f"- {labels['business_type']}: {product.business_type}",
        f"- {labels['location']}: {product.location}",
        f"- {labels['customer']}: {product.customer_segment}",
        f"- {labels['dietary']}: {product.dietary_focus}",
        f"- {labels['price']}: EUR {product.target_price_eur:.2f}",
        "",
        labels["scores"],
        f"- {labels['nutrition_score']}: {report.scores.nutrition_score}/100",
        f"- {labels['quality_score']}: {report.scores.quality_score}/100",
        f"- {labels['market_score']}: {report.scores.market_fit_score}/100",
        f"- {labels['ops_score']}: {report.scores.operational_score}/100",
        f"- {labels['overall_score']}: {report.scores.overall_score}/100",
        "",
        labels["nutrition"],
        f"- {labels['protein']}: {_level(report.nutrition.protein_level, italian)}",
        f"- {labels['carbs']}: {_level(report.nutrition.carbohydrate_level, italian)}",
        f"- {labels['fat']}: {_level(report.nutrition.fat_level, italian)}",
        f"- {labels['vitamins']}: {_level(report.nutrition.vitamin_mineral_signal, italian)}",
        f"- {labels['fiber']}: {_level(report.nutrition.fiber_signal, italian)}",
        f"- {labels['sugar']}: {_level(report.nutrition.sugar_risk, italian)}",
        f"- {labels['salt']}: {_level(report.nutrition.salt_risk, italian)}",
        "",
        labels["risks"],
        labels["allergens"],
        *[f"- {x}" for x in report.risks.allergen_risks],
        "",
        labels["conflicts"],
        *[f"- {x}" for x in report.risks.dietary_conflicts],
        "",
        labels["quality"],
        *[f"- {x}" for x in report.risks.quality_risks],
        "",
        labels["operations"],
        *[f"- {x}" for x in report.risks.operational_risks],
        "",
        labels["positioning"],
        report.positioning,
        "",
        labels["ingredient_notes"],
    ]

    for ingredient, note in report.ingredient_notes.items():
        lines.append(f"- {ingredient}: {note}")

    lines.extend([
        "",
        labels["recommendations"],
        *[f"- {x}" for x in report.recommendations],
        "",
        labels["checklist"],
        *[f"- [ ] {x}" for x in report.launch_checklist],
        "",
    ])
    return "\n".join(lines)
