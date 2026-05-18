from __future__ import annotations

from .models import AgentReport


def report_to_markdown(report: AgentReport) -> str:
    product = report.product
    lines = [
        f"# MenuTaste Report: {product.product_name}",
        "",
        "## Executive Summary",
        report.executive_summary,
        "",
        "## Featherless AI Reasoning",
        report.ai_reasoning,
        "",
        "## Product Context",
        f"- Business type: {product.business_type}",
        f"- Location: {product.location}",
        f"- Customer segment: {product.customer_segment}",
        f"- Dietary focus: {product.dietary_focus}",
        f"- Target price: EUR {product.target_price_eur:.2f}",
        "",
        "## Scores",
        f"- Nutrition score: {report.scores.nutrition_score}/100",
        f"- Quality score: {report.scores.quality_score}/100",
        f"- Market fit score: {report.scores.market_fit_score}/100",
        f"- Operational score: {report.scores.operational_score}/100",
        f"- Overall score: {report.scores.overall_score}/100",
        "",
        "## Nutrition Estimate",
        f"- Protein: {report.nutrition.protein_level}",
        f"- Carbohydrates: {report.nutrition.carbohydrate_level}",
        f"- Fat: {report.nutrition.fat_level}",
        f"- Vitamin/mineral signal: {report.nutrition.vitamin_mineral_signal}",
        f"- Fiber signal: {report.nutrition.fiber_signal}",
        f"- Sugar risk: {report.nutrition.sugar_risk}",
        f"- Salt risk: {report.nutrition.salt_risk}",
        "",
        "## Risks",
        "### Allergens",
        *[f"- {x}" for x in report.risks.allergen_risks],
        "",
        "### Dietary Conflicts",
        *[f"- {x}" for x in report.risks.dietary_conflicts],
        "",
        "### Quality Risks",
        *[f"- {x}" for x in report.risks.quality_risks],
        "",
        "### Operational Risks",
        *[f"- {x}" for x in report.risks.operational_risks],
        "",
        "## Positioning",
        report.positioning,
        "",
        "## Ingredient Notes",
    ]

    for ingredient, note in report.ingredient_notes.items():
        lines.append(f"- {ingredient}: {note}")

    lines.extend([
        "",
        "## Recommendations",
        *[f"- {x}" for x in report.recommendations],
        "",
        "## Launch Checklist",
        *[f"- [ ] {x}" for x in report.launch_checklist],
        "",
    ])
    return "\n".join(lines)
