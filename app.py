from __future__ import annotations

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.menutaste.agent import run_menutaste_agent
from src.menutaste.config import APP_SUBTITLE, APP_TITLE, BUSINESS_TYPES, CUSTOMER_SEGMENTS, DIETARY_FOCUS
from src.menutaste.export_utils import report_to_json
from src.menutaste.models import ProductInput
from src.menutaste.report import report_to_markdown
from src.menutaste.validators import clean_ingredients

load_dotenv()

st.set_page_config(page_title="MenuTaste AI Agent", page_icon="🍽️", layout="wide")

st.markdown(
    """
    <style>
    .main {
        background: #fbfbfd;
    }

    .hero-box {
        padding: 28px 32px;
        border-radius: 22px;
        background: linear-gradient(135deg, #fff7ed 0%, #ecfdf5 100%);
        border: 1px solid #fde7c7;
        margin-bottom: 24px;
    }

    .hero-title {
        font-size: 44px;
        font-weight: 800;
        color: #172033;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 18px;
        color: #4b5563;
        max-width: 900px;
        line-height: 1.5;
    }

    .workflow-card {
        padding: 16px 18px;
        border-radius: 16px;
        background: white;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        height: 100%;
    }

    .score-card {
        padding: 18px;
        border-radius: 18px;
        background: white;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
    }

    .score-label {
        font-size: 13px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .score-value {
        font-size: 34px;
        font-weight: 800;
        color: #111827;
    }

    .section-box {
        padding: 20px 24px;
        border-radius: 18px;
        background: white;
        border: 1px solid #e5e7eb;
        margin-top: 10px;
    }

    div.stButton > button:first-child {
        background: #ef4444;
        color: white;
        border-radius: 12px;
        padding: 0.65rem 1.2rem;
        border: none;
        font-weight: 700;
    }

    div.stButton > button:first-child:hover {
        background: #dc2626;
        color: white;
    }

    div[data-testid="column"] {
        padding-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="hero-box">
        <div class="hero-title">🍽️ {APP_TITLE}</div>
        <div class="hero-subtitle">
            {APP_SUBTITLE}. MenuTaste helps food entrepreneurs evaluate food and drink ideas using
            ingredient analysis, nutrition signals, risk checks, business scoring, and Featherless AI reasoning.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

wf1, wf2, wf3, wf4 = st.columns(4)
with wf1:
    st.markdown('<div class="workflow-card"><b>1. Product Input</b><br>Describe the food idea, ingredients, target customer, price, and location.</div>', unsafe_allow_html=True)
with wf2:
    st.markdown('<div class="workflow-card"><b>2. Local Analysis</b><br>Estimate nutrition signals, allergens, dietary conflicts, and operational risks.</div>', unsafe_allow_html=True)
with wf3:
    st.markdown('<div class="workflow-card"><b>3. Featherless Reasoning</b><br>Send a structured prompt to an open-source model for business-ready advice.</div>', unsafe_allow_html=True)
with wf4:
    st.markdown('<div class="workflow-card"><b>4. Launch Report</b><br>Generate scores, recommendations, checklist, and exportable Markdown/JSON.</div>', unsafe_allow_html=True)

st.divider()

with st.sidebar:
    st.header("🍽️ MenuTaste")
    st.write("AI product analyst for food entrepreneurs.")

    st.markdown("### Demo ideas")
    st.write("- Ethiopian breakfast bowl")
    st.write("- Vegan protein smoothie")
    st.write("- Premium focaccia")
    st.write("- Healthy coffee drink")

    st.markdown("### Agent stack")
    st.write("- Streamlit web app")
    st.write("- Local scoring engine")
    st.write("- Featherless AI reasoning")
    st.write("- Markdown/JSON export")

    st.info("For the hackathon demo, show the Featherless Reasoning tab and Export tab.")

col1, col2 = st.columns(2)

with col1:
    product_name = st.text_input("Product name", value="Ethiopian chickpea breakfast bowl")
    description = st.text_area(
        "Short description",
        value="A warm breakfast bowl with chickpeas, tomato, spinach, olive oil, lemon, and spices.",
        height=100,
    )
    raw_ingredients = st.text_area(
        "Ingredients, separated by commas",
        value="chickpeas, tomato, spinach, olive oil, lemon, salt",
        height=100,
    )
    target_price = st.number_input("Target price in EUR", min_value=1.0, max_value=100.0, value=8.5, step=0.5)

with col2:
    business_type = st.selectbox("Business type", BUSINESS_TYPES)
    location = st.text_input("Location", value="Milan, Italy")
    customer_segment = st.selectbox("Customer segment", CUSTOMER_SEGMENTS)
    dietary_focus = st.selectbox("Dietary focus", DIETARY_FOCUS)
    preparation_complexity = st.selectbox("Preparation complexity", ["Low", "Medium", "High"], index=1)
    language = st.selectbox("Output language", ["English", "Italian"], index=0)

if st.button("Run MenuTaste Agent", type="primary"):
    ingredients = clean_ingredients(raw_ingredients)
    product = ProductInput(
        product_name=product_name,
        description=description,
        ingredients=ingredients,
        business_type=business_type,
        location=location,
        customer_segment=customer_segment,
        dietary_focus=dietary_focus,
        target_price_eur=target_price,
        preparation_complexity=preparation_complexity,
        language=language,
    )

    with st.spinner("Running MenuTaste reasoning workflow..."):
        report = run_menutaste_agent(product)

    st.success("MenuTaste report generated.")

    score_items = [
        ("Overall", report.scores.overall_score),
        ("Nutrition", report.scores.nutrition_score),
        ("Quality", report.scores.quality_score),
        ("Market Fit", report.scores.market_fit_score),
        ("Operations", report.scores.operational_score),
    ]

    score_cols = st.columns(5)
    for col, (label, value) in zip(score_cols, score_items):
        with col:
            st.markdown(
                f"""
                <div class="score-card">
                    <div class="score-label">{label}</div>
                    <div class="score-value">{value}/100</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Summary",
        "Nutrition & Risks",
        "Featherless Reasoning",
        "Recommendations",
        "Export",
    ])
        
    with tab1:
        st.subheader("Executive Summary")
        st.write(report.executive_summary)
        st.subheader("Positioning")
        st.write(report.positioning)

    with tab2:
        st.subheader("Nutrition Estimate")

        nutrition_items = {
            "Protein": report.nutrition.protein_level,
            "Carbohydrates": report.nutrition.carbohydrate_level,
            "Fat": report.nutrition.fat_level,
            "Vitamin/mineral signal": report.nutrition.vitamin_mineral_signal,
            "Fiber signal": report.nutrition.fiber_signal,
            "Sugar risk": report.nutrition.sugar_risk,
            "Salt risk": report.nutrition.salt_risk,
        }

        n_cols = st.columns(4)
        for idx, (label, value) in enumerate(nutrition_items.items()):
            with n_cols[idx % 4]:
                st.markdown(
                    f"""
                    <div class="score-card">
                        <div class="score-label">{label}</div>
                        <div class="score-value" style="font-size:24px;">{value}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.subheader("Risks")
        st.write("Allergens:", ", ".join(report.risks.allergen_risks))
        st.write("Dietary conflicts:", ", ".join(report.risks.dietary_conflicts))
        st.write("Quality risks:", ", ".join(report.risks.quality_risks))
        st.write("Operational risks:", ", ".join(report.risks.operational_risks))

        st.subheader("Ingredient Notes")

        for ingredient, note in report.ingredient_notes.items():
            st.markdown(
                f"""
                <div class="section-box">
                    <b>{ingredient.title()}</b><br>
                    <span style="color:#4b5563;">{note}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    
    with tab3:
        st.subheader("AI Reasoning")
        st.write(report.ai_reasoning)

    with tab4:
        st.subheader("Recommendations")
        for rec in report.recommendations:
            st.markdown(f"- {rec}")

        st.subheader("Launch Checklist")
        for item in report.launch_checklist:
            st.checkbox(item, value=False)

    with tab5:
        markdown_report = report_to_markdown(report)
        json_report = report_to_json(report)

        st.download_button(
            "Download Markdown Report",
            markdown_report,
            file_name="menutaste_report.md",
            mime="text/markdown",
        )
        st.download_button(
            "Download JSON Report",
            json_report,
            file_name="menutaste_report.json",
            mime="application/json",
        )
        st.text_area("Markdown Preview", markdown_report, height=350)
