from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI


SYSTEM_PROMPT = """
You are MenuTaste, a domain-specialized AI agent for food entrepreneurs.

Your job is to analyze a food or drink product idea and produce practical business-ready advice.

You must evaluate:
1. nutrition positioning
2. ingredient quality
3. taste and customer appeal
4. allergen and dietary risks
5. operational complexity
6. pricing and market fit
7. launch readiness

Rules:
- Do not invent exact calories or medical claims.
- Do not say the product is healthy unless the evidence supports it.
- Be practical for small food businesses, cafes, restaurants, cloud kitchens, and packaged food startups.
- Focus on actions the entrepreneur can take this week.
- Keep the answer structured, concise, and useful for a demo.
"""


def featherless_enabled() -> bool:
    return os.getenv("USE_FEATHERLESS", "true").lower() in {"1", "true", "yes"} and bool(os.getenv("FEATHERLESS_API_KEY"))


def get_client() -> OpenAI:
    return OpenAI(
        base_url=os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1"),
        api_key=os.environ["FEATHERLESS_API_KEY"],
    )


def generate_ai_reasoning(product_summary: str, deterministic_summary: str) -> str:
    if not featherless_enabled():
        return (
            "Featherless is not configured, so MenuTaste used deterministic local reasoning. "
            "Add FEATHERLESS_API_KEY to enable model-generated strategic analysis."
        )

    model = os.getenv("FEATHERLESS_MODEL", "Qwen/Qwen2.5-7B-Instruct")
    client = get_client()

    user_prompt = f"""
    Analyze this food or drink concept as MenuTaste.

    PRODUCT DETAILS
    {product_summary}

    LOCAL ANALYSIS RESULTS
    {deterministic_summary}

    Return exactly these sections:

    1. Product Quality Verdict
    Give a clear verdict: Strong, Promising, Risky, or Needs Refinement.

    2. Nutrition Positioning
    Explain the nutrition strengths and weaknesses without giving fake exact values.

    3. Taste and Customer Appeal
    Explain why customers may or may not like it.

    4. Risk Review
    Mention allergen, dietary, sugar, salt, and operational risks.

    5. Market Positioning
    Explain the best target customer and selling message.

    6. Improvement Actions
    Give 5 concrete improvements.

    7. Launch Test
    Give one simple test the entrepreneur can run in 7 days.

    Keep the tone professional, practical, and startup-friendly.
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=700,
        )
        return response.choices[0].message.content or "No AI reasoning was returned."
    except Exception as exc:
        return (
            "Featherless call failed, so MenuTaste used local reasoning only. "
            f"Error: {type(exc).__name__}: {exc}"
        )
