from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv
from pydantic import ValidationError

from src.menutaste.agent import run_menutaste_agent
from src.menutaste.config import APP_SUBTITLE, APP_TITLE, BUSINESS_TYPES, CUSTOMER_SEGMENTS, DIETARY_FOCUS
from src.menutaste.export_utils import report_to_json
from src.menutaste.models import ProductInput
from src.menutaste.report import report_to_markdown
from src.menutaste.validators import clean_ingredients

load_dotenv()

st.set_page_config(page_title="MenuTaste AI Agent", page_icon="🍽️", layout="wide")

DEMO_SCENARIOS = {
    "Ethiopian breakfast bowl": {
        "product_name": "Ethiopian chickpea breakfast bowl",
        "description": "A warm breakfast bowl with chickpeas, tomato, spinach, olive oil, lemon, and spices.",
        "ingredients": "chickpeas, tomato, spinach, olive oil, lemon, salt",
        "business_type": "Cafe",
        "location": "Milan, Italy",
        "customer_segment": "Office workers",
        "dietary_focus": "Low sugar",
        "target_price": 8.5,
        "complexity": "High",
    },
    "Vegan protein smoothie": {
        "product_name": "Green vegan protein smoothie",
        "description": "A ready-to-go smoothie for gym customers and busy office workers.",
        "ingredients": "banana, spinach, almond milk, peanut butter, oats, chia seeds",
        "business_type": "Juice or drink bar",
        "location": "Milan, Italy",
        "customer_segment": "Fitness-focused customers",
        "dietary_focus": "Vegan",
        "target_price": 6.5,
        "complexity": "Low",
    },
    "Premium focaccia": {
        "product_name": "Premium tomato and olive focaccia",
        "description": "A premium bakery item for lunch and aperitivo customers.",
        "ingredients": "wheat flour, olive oil, tomato, cheese, salt, herbs",
        "business_type": "Bakery",
        "location": "Milan, Italy",
        "customer_segment": "Premium food lovers",
        "dietary_focus": "None",
        "target_price": 5.5,
        "complexity": "Medium",
    },
    "Healthy coffee drink": {
        "product_name": "Low-sugar oat coffee shake",
        "description": "A cold coffee drink positioned as a lighter alternative to sweet coffee beverages.",
        "ingredients": "coffee, oat milk, banana, cocoa, cinnamon",
        "business_type": "Cafe",
        "location": "Milan, Italy",
        "customer_segment": "Office workers",
        "dietary_focus": "Low sugar",
        "target_price": 4.8,
        "complexity": "Low",
    },
}


def option_index(options: list[str], value: str) -> int:
    return options.index(value) if value in options else 0


def score_tone(value: int) -> str:
    if value >= 80:
        return "Strong"
    if value >= 65:
        return "Ready to test"
    return "Needs work"


def render_score_card(label: str, value: int) -> None:
    tone = score_tone(value)
    st.markdown(
        f"""
        <div class="score-card">
            <div class="score-label">{label}</div>
            <div class="score-value">{value}/100</div>
            <div class="score-tone">{tone}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_small_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="mini-card">
            <div class="score-label">{label}</div>
            <div class="mini-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_card(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="section-box">
            <b>{title}</b><br>
            <span>{body}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def featherless_status() -> str:
    if os.getenv("USE_FEATHERLESS", "true").lower() not in {"1", "true", "yes"}:
        return "Disabled"
    if not os.getenv("FEATHERLESS_API_KEY"):
        return "Missing API key"
    return "Connected"


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    :root {
        --page-bg: #f3f7f2;
        --sidebar-bg: #e4eef8;
        --text-main: #102033;
        --text-soft: #334155;
        --card-border: #d8e2ee;
        --card-shadow: 0 8px 20px rgba(15, 23, 42, 0.07);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background: var(--page-bg);
        color: var(--text-main);
        overflow-x: hidden;
    }

    header[data-testid="stHeader"] {
        background: rgba(243, 247, 242, 0.96);
    }

    section[data-testid="stSidebar"] {
        background: var(--sidebar-bg);
        border-right: 1px solid #c7d8ea;
    }

    section[data-testid="stSidebar"] * {
        font-size: clamp(14px, 0.9vw, 18px);
        color: var(--text-main);
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #0f172a;
        font-weight: 850;
    }

    .block-container {
        padding-top: clamp(2.5rem, 5vw, 4.8rem) !important;
        padding-bottom: 3.2rem;
        max-width: min(1520px, 92vw);
        margin-left: auto;
        margin-right: auto;
        overflow-x: hidden;
    }

    .main .block-container {
        overflow-x: hidden;
    }

    h1, h2, h3 {
        color: #0f172a;
        letter-spacing: -0.03em;
    }

    p, li, label, span, div {
        font-size: clamp(14px, 1vw, 18px);
        line-height: 1.6;
    }

    [data-testid="stMarkdownContainer"],
    [data-testid="stCaptionContainer"],
    .stTabs,
    .stTextInput,
    .stTextArea,
    .stNumberInput,
    .stSelectbox {
        color: var(--text-main) !important;
    }

    label,
    [data-testid="stWidgetLabel"] p {
        font-size: clamp(14px, 0.95vw, 18px) !important;
        font-weight: 750 !important;
        color: #1f2937 !important;
    }

    input, textarea, select {
        font-size: clamp(14px, 1vw, 18px) !important;
    }

    .hero-box {
        padding: clamp(26px, 3.2vw, 40px);
        border-radius: 28px;
        background: linear-gradient(135deg, #fff7ed 0%, #eefdf4 55%, #e8f4ff 100%);
        border: 1px solid #fdba74;
        margin-bottom: 24px;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
        overflow: hidden;
    }

    .hero-title {
        font-size: clamp(32px, 4vw, 50px);
        font-weight: 900;
        color: #0b1220;
        margin-bottom: 14px;
        letter-spacing: -0.055em;
        line-height: 1.05;
    }

    .hero-subtitle {
        font-size: clamp(15px, 1.35vw, 18px);
        color: #243447;
        max-width: 1080px;
        line-height: 1.65;
        font-weight: 500;
    }

    .badge-row {
        margin-top: 22px;
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
    }

    .badge {
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid #dbe4ef;
        color: #233247;
        font-size: clamp(14px, 0.9vw, 18px);
        font-weight: 800;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        white-space: nowrap;
    }

    .workflow-card {
        padding: clamp(18px, 1.6vw, 22px);
        border-radius: 20px;
        background: #ffffff;
        border: 1px solid #d9e2ec;
        box-shadow: var(--card-shadow);
        min-height: 112px;
        color: #1e293b;
        line-height: 1.55;
        font-size: clamp(14px, 1vw, 16px);
    }

    .workflow-card b {
        color: #0f172a;
        font-size: clamp(15px, 1.05vw, 17px);
        font-weight: 850;
    }

    .score-card {
        padding: clamp(18px, 1.7vw, 24px);
        border-radius: 22px;
        background: #ffffff;
        border: 1px solid var(--card-border);
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
        min-height: 126px;
    }

    .score-label {
        font-size: clamp(12px, 0.8vw, 15px);
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        font-weight: 850;
        margin-bottom: 8px;
    }

    .score-value {
        font-size: clamp(28px, 3vw, 39px);
        font-weight: 900;
        color: #020617;
        letter-spacing: -0.055em;
        line-height: 1.1;
    }

    .score-tone {
        margin-top: 10px;
        font-size: clamp(14px, 0.9vw, 18px);
        color: #475569;
        font-weight: 800;
    }

    .mini-card {
        padding: clamp(18px, 1.6vw, 22px) clamp(18px, 1.7vw, 24px);
        border-radius: 20px;
        background: #ffffff;
        border: 1px solid var(--card-border);
        box-shadow: 0 7px 18px rgba(15, 23, 42, 0.06);
        min-height: 108px;
    }

    .mini-value {
        font-size: clamp(20px, 2vw, 27px);
        font-weight: 900;
        color: #0f172a;
        line-height: 1.2;
        overflow-wrap: anywhere;
    }

    .section-box {
        padding: clamp(18px, 1.7vw, 22px) clamp(20px, 2vw, 26px);
        border-radius: 20px;
        background: #ffffff;
        border: 1px solid var(--card-border);
        margin: 12px 0;
        color: #243447;
        box-shadow: 0 5px 16px rgba(15, 23, 42, 0.05);
        line-height: 1.65;
        font-size: clamp(14px, 1vw, 16px);
    }

    .section-box b {
        color: #0f172a;
        font-size: clamp(15px, 1.05vw, 17px);
    }

    .risk-box {
        padding: clamp(16px, 1.5vw, 18px) clamp(18px, 1.7vw, 22px);
        border-radius: 18px;
        background: #fff7ed;
        border: 1px solid #fdba74;
        margin-bottom: 12px;
        color: #263445;
        font-size: clamp(14px, 1vw, 16px);
        line-height: 1.6;
    }

    .risk-box b {
        color: #9a3412;
        font-size: clamp(15px, 1.05vw, 17px);
    }

    .success-box {
        padding: 18px 22px;
        border-radius: 18px;
        background: #dcfce7;
        border: 1px solid #86efac;
        color: #166534;
        font-size: clamp(15px, 1.05vw, 17px);
        font-weight: 850;
        margin: 18px 0 22px 0;
    }

    div.stButton > button:first-child {
        background: #ef4444;
        color: white;
        border-radius: 16px;
        padding: 0.9rem 1.35rem;
        border: none;
        font-size: clamp(14px, 1vw, 16px);
        font-weight: 850;
        box-shadow: 0 10px 22px rgba(239, 68, 68, 0.28);
    }

    div.stButton > button:first-child:hover {
        background: #dc2626;
        color: white;
        transform: translateY(-1px);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #cbd5e1;
        overflow-x: auto;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: clamp(14px, 1vw, 18px);
        font-weight: 750;
        padding: 12px 10px;
        white-space: nowrap;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-baseweb="select"] {
        background: #edf2f7 !important;
        border-radius: 12px !important;
        border: 1px solid #d7e0ea !important;
    }

    div[data-testid="column"] {
        padding-bottom: 14px;
    }

    hr {
        border-color: #cbd5e1;
        margin: 2.0rem 0;
    }

    @media (max-width: 900px) {
        .hero-box {
            padding: 28px 24px;
        }

        .workflow-card,
        .score-card,
        .mini-card,
        .section-box {
            padding: 18px;
        }

        .badge {
            font-size: 12px;
            padding: 6px 10px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("🍽️ MenuTaste")
    st.write("AI product analyst for food entrepreneurs.")

    selected_demo = st.selectbox("Choose a demo scenario", list(DEMO_SCENARIOS.keys()))
    demo = DEMO_SCENARIOS[selected_demo]

    st.markdown("### Agent status")
    status = featherless_status()
    if status == "Connected":
        st.success("Featherless connected")
    elif status == "Disabled":
        st.warning("Featherless disabled")
    else:
        st.warning("Featherless key missing")

    st.markdown("### Agent stack")
    st.write("- Streamlit web app")
    st.write("- Local scoring engine")
    st.write("- Featherless AI reasoning")
    st.write("- Markdown/JSON export")

    st.info("Demo tip: show Summary, Nutrition & Risks, Featherless Reasoning, and Export.")

st.markdown(
    f"""
    <div class="hero-box">
        <div class="hero-title">🍽️ {APP_TITLE}</div>
        <div class="hero-subtitle">
            {APP_SUBTITLE}. MenuTaste turns a food or drink idea into a clear product-quality,
            nutrition, risk, market-fit, and launch-readiness report for small food businesses.
        </div>
        <div class="badge-row">
            <span class="badge">Featherless AI</span>
            <span class="badge">Food product analysis</span>
            <span class="badge">Risk detection</span>
            <span class="badge">Launch checklist</span>
            <span class="badge">Markdown and JSON export</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

wf1, wf2, wf3, wf4 = st.columns(4)
with wf1:
    st.markdown('<div class="workflow-card"><b>1. Product Input</b><br>Collect product, ingredients, target customer, price, location, and dietary goal.</div>', unsafe_allow_html=True)
with wf2:
    st.markdown('<div class="workflow-card"><b>2. Local Analysis</b><br>Estimate nutrition signals, allergens, dietary conflicts, and operational risks.</div>', unsafe_allow_html=True)
with wf3:
    st.markdown('<div class="workflow-card"><b>3. Featherless Reasoning</b><br>Send a structured prompt to an open-source model for product strategy.</div>', unsafe_allow_html=True)
with wf4:
    st.markdown('<div class="workflow-card"><b>4. Launch Report</b><br>Generate scores, recommendations, pilot checklist, and exportable reports.</div>', unsafe_allow_html=True)

st.divider()

st.markdown("### Product analysis input")
st.caption("Select a demo scenario from the sidebar or edit the fields below.")

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        product_name = st.text_input("Product name", value=demo["product_name"])
        description = st.text_area("Short description", value=demo["description"], height=105)
        raw_ingredients = st.text_area("Ingredients, separated by commas", value=demo["ingredients"], height=105)
        target_price = st.number_input("Target price in EUR", min_value=1.0, max_value=100.0, value=float(demo["target_price"]), step=0.5)

    with col2:
        business_type = st.selectbox("Business type", BUSINESS_TYPES, index=option_index(BUSINESS_TYPES, demo["business_type"]))
        location = st.text_input("Location", value=demo["location"])
        customer_segment = st.selectbox("Customer segment", CUSTOMER_SEGMENTS, index=option_index(CUSTOMER_SEGMENTS, demo["customer_segment"]))
        dietary_focus = st.selectbox("Dietary focus", DIETARY_FOCUS, index=option_index(DIETARY_FOCUS, demo["dietary_focus"]))
        preparation_complexity = st.selectbox("Preparation complexity", ["Low", "Medium", "High"], index=option_index(["Low", "Medium", "High"], demo["complexity"]))
        language = st.selectbox("Output language", ["English", "Italian"], index=0)


run_clicked = st.button("Run MenuTaste Agent", type="primary")

if run_clicked:
    ingredients = clean_ingredients(raw_ingredients)

    if not ingredients:
        st.error("Please add at least one ingredient.")
        st.stop()

    try:
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
    except ValidationError as exc:
        st.error("Please fix the product input before running the agent.")
        st.code(str(exc))
        st.stop()

    with st.spinner("Running MenuTaste reasoning workflow..."):
        report = run_menutaste_agent(product)

    st.markdown('<div class="success-box">MenuTaste report generated.</div>', unsafe_allow_html=True)

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
            render_score_card(label, value)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Summary",
        "Nutrition & Risks",
        "Featherless Reasoning",
        "Recommendations",
        "Export",
    ])

    with tab1:
        st.subheader("Executive Summary")
        render_info_card("Business-ready summary", report.executive_summary)

        st.subheader("Product Positioning")
        render_info_card("Suggested market message", report.positioning)

        c1, c2, c3 = st.columns(3)
        with c1:
            render_small_card("Business type", report.product.business_type)
        with c2:
            render_small_card("Target customer", report.product.customer_segment)
        with c3:
            render_small_card("Target price", f"EUR {report.product.target_price_eur:.2f}")

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
                render_small_card(label, value)

        st.subheader("Risk Review")
        risk_items = {
            "Allergens": ", ".join(report.risks.allergen_risks),
            "Dietary conflicts": ", ".join(report.risks.dietary_conflicts),
            "Quality risks": ", ".join(report.risks.quality_risks),
            "Operational risks": ", ".join(report.risks.operational_risks),
        }
        for label, value in risk_items.items():
            st.markdown(
                f"""
                <div class="risk-box">
                    <b>{label}</b><br>{value}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.subheader("Ingredient Notes")
        for ingredient, note in report.ingredient_notes.items():
            render_info_card(ingredient.title(), note)

    with tab3:
        st.subheader("Featherless AI Reasoning")
        st.caption("This section is generated from the structured prompt sent to the Featherless model.")
        st.markdown(report.ai_reasoning)

    with tab4:
        st.subheader("Recommended Actions")
        for idx, rec in enumerate(report.recommendations, start=1):
            render_info_card(f"Action {idx}", rec)

        st.subheader("Launch Checklist")
        for idx, item in enumerate(report.launch_checklist):
            st.checkbox(item, value=False, key=f"launch_{idx}_{item}")

    with tab5:
        markdown_report = report_to_markdown(report)
        json_report = report_to_json(report)

        st.subheader("Export Report")
        e1, e2 = st.columns(2)
        with e1:
            st.download_button(
                "Download Markdown Report",
                markdown_report,
                file_name="menutaste_report.md",
                mime="text/markdown",
            )
        with e2:
            st.download_button(
                "Download JSON Report",
                json_report,
                file_name="menutaste_report.json",
                mime="application/json",
            )

        st.subheader("Markdown Preview")
        st.text_area("Report content", markdown_report, height=420, label_visibility="collapsed")
else:
    st.markdown(
        """
        <div class="section-box">
            <b>Ready to run.</b><br>
            Choose a demo scenario, edit the details, and click <b>Run MenuTaste Agent</b>.
            The app will combine local scoring with Featherless model reasoning.
        </div>
        """,
        unsafe_allow_html=True,
    )
