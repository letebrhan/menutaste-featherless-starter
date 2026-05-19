from __future__ import annotations

import os

import streamlit as st
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
- Always respond only in the requested output language.
"""


def get_setting(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name)
        if value is not None and str(value).strip():
            return str(value)
    except Exception:
        pass

    return os.getenv(name, default)


def featherless_enabled() -> bool:
    use_featherless = get_setting("USE_FEATHERLESS", "true").lower() in {
        "1",
        "true",
        "yes",
    }
    api_key = get_setting("FEATHERLESS_API_KEY", "")
    return use_featherless and bool(api_key)


def get_client() -> OpenAI:
    return OpenAI(
        base_url=get_setting("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1"),
        api_key=get_setting("FEATHERLESS_API_KEY"),
    )


def _section_titles(output_language: str) -> str:
    if output_language.lower().startswith("italian"):
        return """
1. Verdetto sulla qualita del prodotto
2. Posizionamento nutrizionale
3. Gusto e interesse dei clienti
4. Revisione dei rischi
5. Posizionamento di mercato
6. Azioni di miglioramento
7. Test di lancio
"""
    return """
1. Product Quality Verdict
2. Nutrition Positioning
3. Taste and Customer Appeal
4. Risk Review
5. Market Positioning
6. Improvement Actions
7. Launch Test
"""


def generate_ai_reasoning(
    product_summary: str,
    deterministic_summary: str,
    output_language: str = "English",
) -> str:
    language = output_language or "English"
    italian = language.lower().startswith("italian")

    if not featherless_enabled():
        if italian:
            return (
                "Featherless non e configurato, quindi MenuTaste ha usato solo il ragionamento locale deterministico. "
                "Aggiungi FEATHERLESS_API_KEY per abilitare l'analisi strategica generata dal modello."
            )
        return (
            "Featherless is not configured, so MenuTaste used deterministic local reasoning. "
            "Add FEATHERLESS_API_KEY to enable model-generated strategic analysis."
        )

    model = get_setting("FEATHERLESS_MODEL", "deepseek-ai/DeepSeek-V3-0324")
    client = get_client()
    section_titles = _section_titles(language)

    if italian:
        language_rule = """
REGOLA LINGUA OBBLIGATORIA:
Scrivi tutta la risposta in italiano.
Non usare titoli di sezione in inglese.
Traduci anche verdict, rischi, raccomandazioni e test di lancio.
Puoi lasciare invariati solo brand name, product name o termini tecnici necessari.
"""
        detail_instruction = """
Analizza questo concept food o drink come MenuTaste.

DETTAGLI PRODOTTO
{product_summary}

RISULTATI ANALISI LOCALE
{deterministic_summary}

Restituisci esattamente queste sezioni in italiano:
{section_titles}

Per ogni sezione:
- usa tono professionale, pratico e startup-friendly
- non inventare calorie o valori nutrizionali esatti
- fornisci consigli concreti utilizzabili questa settimana
""".format(
            product_summary=product_summary,
            deterministic_summary=deterministic_summary,
            section_titles=section_titles,
        )
    else:
        language_rule = """
MANDATORY LANGUAGE RULE:
Write the entire response in English.
Do not mix languages except for brand names, product names, or technical terms that should remain unchanged.
"""
        detail_instruction = """
Analyze this food or drink concept as MenuTaste.

PRODUCT DETAILS
{product_summary}

LOCAL ANALYSIS RESULTS
{deterministic_summary}

Return exactly these sections in English:
{section_titles}

For each section:
- use a professional, practical, startup-friendly tone
- do not invent exact calories or nutrition values
- provide concrete advice the entrepreneur can use this week
""".format(
            product_summary=product_summary,
            deterministic_summary=deterministic_summary,
            section_titles=section_titles,
        )

    user_prompt = f"{language_rule}\n{detail_instruction}"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=900,
        )
        return response.choices[0].message.content or (
            "Nessun ragionamento AI restituito."
            if italian
            else "No AI reasoning was returned."
        )
    except Exception as exc:
        if italian:
            return (
                "La chiamata a Featherless non e riuscita, quindi MenuTaste ha usato solo il ragionamento locale. "
                f"Errore: {type(exc).__name__}: {exc}"
            )
        return (
            "Featherless call failed, so MenuTaste used local reasoning only. "
            f"Error: {type(exc).__name__}: {exc}"
        )