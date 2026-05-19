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

UI_TEXT = {
    "English": {
        "sidebar_title": "🍽️ MenuTaste",
        "sidebar_subtitle": "AI product analyst for food entrepreneurs.",
        "language_label": "Language",
        "demo_label": "Choose a demo scenario",
        "agent_status": "Agent status",
        "connected": "Featherless connected",
        "disabled": "Featherless disabled",
        "missing_key": "Featherless key missing",
        "agent_stack": "Agent stack",
        "stack_items": ["Streamlit web app", "Local scoring engine", "Featherless AI reasoning", "Markdown/JSON export"],
        "demo_tip": "Demo tip: show Summary, Nutrition & Risks, Featherless Reasoning, and Export.",
        "hero_title": "🍽️ MenuTaste AI Agent",
        "hero_subtitle": "Featherless-powered quality, nutrition, and launch copilot for food entrepreneurs. MenuTaste turns a food or drink idea into a clear product-quality, nutrition, risk, market-fit, and launch-readiness report for small food businesses.",
        "badges": ["Featherless AI", "Food product analysis", "Risk detection", "Launch checklist", "Markdown and JSON export"],
        "workflow": [
            ("1. Product Input", "Collect product, ingredients, target customer, price, location, and dietary goal."),
            ("2. Local Analysis", "Estimate nutrition signals, allergens, dietary conflicts, and operational risks."),
            ("3. Featherless Reasoning", "Send a structured prompt to an open-source model for product strategy."),
            ("4. Launch Report", "Generate scores, recommendations, pilot checklist, and exportable reports."),
        ],
        "input_title": "Product analysis input",
        "input_caption": "Select a demo scenario from the sidebar or edit the fields below.",
        "product_name": "Product name",
        "description": "Short description",
        "ingredients": "Ingredients, separated by commas",
        "target_price": "Target price in EUR",
        "business_type": "Business type",
        "location": "Location",
        "customer_segment": "Customer segment",
        "dietary_focus": "Dietary focus",
        "complexity": "Preparation complexity",
        "run": "Run MenuTaste Agent",
        "report_generated": "MenuTaste report generated.",
        "tabs": ["Summary", "Nutrition & Risks", "Featherless Reasoning", "Recommendations", "Export"],
        "scores": ["Overall", "Nutrition", "Quality", "Market Fit", "Operations"],
        "tones": {"Strong": "Strong", "Ready to test": "Ready to test", "Needs work": "Needs work"},
        "summary_title": "Executive Summary",
        "summary_card": "Business-ready summary",
        "positioning_title": "Product Positioning",
        "positioning_card": "Suggested market message",
        "business_type_card": "Business type",
        "target_customer_card": "Target customer",
        "target_price_card": "Target price",
        "nutrition_title": "Nutrition Estimate",
        "risk_title": "Risk Review",
        "ingredient_notes": "Ingredient Notes",
        "risk_labels": ["Allergens", "Dietary conflicts", "Quality risks", "Operational risks"],
        "ai_title": "Featherless AI Reasoning",
        "ai_caption": "This section is generated from the structured prompt sent to the Featherless model.",
        "actions_title": "Recommended Actions",
        "action": "Action",
        "checklist_title": "Launch Checklist",
        "export_title": "Export Report",
        "download_md": "Download Markdown Report",
        "download_json": "Download JSON Report",
        "markdown_preview": "Markdown Preview",
        "report_content": "Report content",
        "ready_title": "Ready to run.",
        "ready_body": "Choose a demo scenario, edit the details, and click <b>Run MenuTaste Agent</b>. The app will combine local scoring with Featherless model reasoning.",
        "validation_ingredients": "Please add at least one ingredient.",
        "validation_input": "Please fix the product input before running the agent.",
    },
    "Italian": {
        "sidebar_title": "🍽️ MenuTaste",
        "sidebar_subtitle": "Analista AI di prodotto per imprenditori del food.",
        "language_label": "Lingua",
        "demo_label": "Scegli uno scenario demo",
        "agent_status": "Stato agente",
        "connected": "Featherless connesso",
        "disabled": "Featherless disattivato",
        "missing_key": "Chiave Featherless mancante",
        "agent_stack": "Stack agente",
        "stack_items": ["App web Streamlit", "Motore di scoring locale", "Ragionamento AI Featherless", "Export Markdown/JSON"],
        "demo_tip": "Suggerimento demo: mostra Riepilogo, Nutrizione e rischi, Ragionamento Featherless ed Export.",
        "hero_title": "🍽️ MenuTaste AI Agent",
        "hero_subtitle": "Copilota Featherless per qualità, nutrizione e lancio per imprenditori del food. MenuTaste trasforma un'idea food o drink in un report chiaro su qualità del prodotto, nutrizione, rischi, market fit e prontezza al lancio per piccole imprese alimentari.",
        "badges": ["Featherless AI", "Analisi prodotto food", "Rilevamento rischi", "Checklist di lancio", "Export Markdown e JSON"],
        "workflow": [
            ("1. Input prodotto", "Raccoglie prodotto, ingredienti, cliente target, prezzo, luogo e obiettivo dietetico."),
            ("2. Analisi locale", "Stima segnali nutrizionali, allergeni, conflitti dietetici e rischi operativi."),
            ("3. Ragionamento Featherless", "Invia un prompt strutturato a un modello open-source per la strategia prodotto."),
            ("4. Report di lancio", "Genera punteggi, raccomandazioni, checklist pilota e report esportabili."),
        ],
        "input_title": "Input analisi prodotto",
        "input_caption": "Seleziona uno scenario demo dalla sidebar oppure modifica i campi qui sotto.",
        "product_name": "Nome prodotto",
        "description": "Breve descrizione",
        "ingredients": "Ingredienti, separati da virgole",
        "target_price": "Prezzo target in EUR",
        "business_type": "Tipo di attività",
        "location": "Località",
        "customer_segment": "Segmento clienti",
        "dietary_focus": "Focus dietetico",
        "complexity": "Complessità di preparazione",
        "run": "Esegui agente MenuTaste",
        "report_generated": "Report MenuTaste generato.",
        "tabs": ["Riepilogo", "Nutrizione e rischi", "Ragionamento Featherless", "Raccomandazioni", "Export"],
        "scores": ["Totale", "Nutrizione", "Qualità", "Market fit", "Operazioni"],
        "tones": {"Strong": "Forte", "Ready to test": "Pronto da testare", "Needs work": "Da migliorare"},
        "summary_title": "Riepilogo esecutivo",
        "summary_card": "Sintesi pronta per il business",
        "positioning_title": "Posizionamento prodotto",
        "positioning_card": "Messaggio di mercato suggerito",
        "business_type_card": "Tipo di attività",
        "target_customer_card": "Cliente target",
        "target_price_card": "Prezzo target",
        "nutrition_title": "Stima nutrizionale",
        "risk_title": "Revisione rischi",
        "ingredient_notes": "Note sugli ingredienti",
        "risk_labels": ["Allergeni", "Conflitti dietetici", "Rischi qualità", "Rischi operativi"],
        "ai_title": "Ragionamento AI Featherless",
        "ai_caption": "Questa sezione è generata dal prompt strutturato inviato al modello Featherless.",
        "actions_title": "Azioni raccomandate",
        "action": "Azione",
        "checklist_title": "Checklist di lancio",
        "export_title": "Esporta report",
        "download_md": "Scarica report Markdown",
        "download_json": "Scarica report JSON",
        "markdown_preview": "Anteprima Markdown",
        "report_content": "Contenuto report",
        "ready_title": "Pronto per l'analisi.",
        "ready_body": "Scegli uno scenario demo, modifica i dettagli e clicca <b>Esegui agente MenuTaste</b>. L'app combinerà scoring locale e ragionamento del modello Featherless.",
        "validation_ingredients": "Aggiungi almeno un ingrediente.",
        "validation_input": "Correggi l'input del prodotto prima di eseguire l'agente.",
    },
}

TRANSLATIONS = {
    "Italian": {
        "Ethiopian breakfast bowl": "Bowl etiope per colazione",
        "Vegan protein smoothie": "Smoothie proteico vegano",
        "Premium focaccia": "Focaccia premium",
        "Healthy coffee drink": "Bevanda al caffè leggera",
        "Cafe": "Caffetteria",
        "Restaurant": "Ristorante",
        "Cloud kitchen": "Cloud kitchen",
        "Catering": "Catering",
        "Food truck": "Food truck",
        "Packaged food product": "Prodotto alimentare confezionato",
        "Juice or drink bar": "Juice bar o drink bar",
        "Bakery": "Panetteria",
        "Students": "Studenti",
        "Office workers": "Impiegati",
        "Families": "Famiglie",
        "Fitness-focused customers": "Clienti orientati al fitness",
        "Tourists": "Turisti",
        "Premium food lovers": "Clienti premium amanti del food",
        "Budget-conscious customers": "Clienti attenti al budget",
        "None": "Nessuno",
        "High protein": "Alto contenuto proteico",
        "Low sugar": "Basso zucchero",
        "Vegetarian": "Vegetariano",
        "Vegan": "Vegano",
        "Gluten-free": "Senza glutine",
        "Dairy-free": "Senza latticini",
        "Halal-friendly": "Adatto halal",
        "Low": "Bassa",
        "Medium": "Media",
        "High": "Alta",
        "English": "Inglese",
        "Italian": "Italiano",
        "Protein": "Proteine",
        "Carbohydrates": "Carboidrati",
        "Fat": "Grassi",
        "Vitamin/mineral signal": "Segnale vitamine/minerali",
        "Fiber signal": "Segnale fibre",
        "Sugar risk": "Rischio zucchero",
        "Salt risk": "Rischio sale",
    },
    "English": {},
}

ITALIAN_DEMO_FIELDS = {
    "Ethiopian breakfast bowl": {
        "product_name": "Bowl etiope di ceci per colazione",
        "description": "Una bowl calda per colazione con ceci, pomodoro, spinaci, olio d'oliva, limone e spezie.",
    },
    "Vegan protein smoothie": {
        "product_name": "Smoothie proteico verde vegano",
        "description": "Uno smoothie pronto da bere per clienti fitness e lavoratori impegnati.",
    },
    "Premium focaccia": {
        "product_name": "Focaccia premium con pomodoro e olive",
        "description": "Un prodotto da forno premium per clienti del pranzo e dell'aperitivo.",
    },
    "Healthy coffee drink": {
        "product_name": "Shake al caffè d'avena a basso zucchero",
        "description": "Una bevanda fredda al caffè posizionata come alternativa più leggera alle bevande dolci al caffè.",
    },
}


def tr(value: str, language: str) -> str:
    return TRANSLATIONS.get(language, {}).get(value, value)


def reverse_tr(value: str, language: str) -> str:
    if language == "English":
        return value
    mapping = TRANSLATIONS.get(language, {})
    reverse = {translated: original for original, translated in mapping.items()}
    return reverse.get(value, value)


def display_options(options: list[str], language: str) -> list[str]:
    return [tr(option, language) for option in options]


def translated_demo_values(scenario_key: str, language: str) -> dict:
    demo = DEMO_SCENARIOS[scenario_key].copy()
    if language == "Italian":
        demo.update(ITALIAN_DEMO_FIELDS.get(scenario_key, {}))
    return demo


def option_index(options: list[str], value: str) -> int:
    return options.index(value) if value in options else 0


def localized_value(value: str, language: str) -> str:
    return tr(value, language)


def localized_list(values: list[str], language: str) -> list[str]:
    return [tr(value, language) for value in values]


def score_tone(value: int) -> str:
    if value >= 80:
        return "Strong"
    if value >= 65:
        return "Ready to test"
    return "Needs work"


def render_score_card(label: str, value: int, language: str) -> None:
    tone = UI_TEXT[language]["tones"][score_tone(value)]
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
        font-size: clamp(25px, 3vw, 36px);
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

    /* Main run button */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #16a34a 0%, #0f766e 100%);
        color: white;
        border-radius: 16px;
        padding: 0.9rem 1.35rem;
        border: none;
        font-size: clamp(14px, 1vw, 16px);
        font-weight: 850;
        box-shadow: 0 10px 22px rgba(22, 163, 74, 0.26);
    }

    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #15803d 0%, #0f766e 100%);
        color: white;
        transform: translateY(-1px);
    }

    /* Export download buttons */
    div.stDownloadButton > button {
        background: #2563eb;
        color: white;
        border-radius: 14px;
        padding: 0.8rem 1.2rem;
        border: none;
        font-size: clamp(14px, 1vw, 16px);
        font-weight: 800;
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.22);
    }

    div.stDownloadButton > button:hover {
        background: #1d4ed8;
        color: white;
        transform: translateY(-1px);
    }

    /* Tabs container */
    .stTabs [data-baseweb="tab-list"] {
        gap: clamp(8px, 1vw, 14px) !important;
        border-bottom: 1px solid #cbd5e1 !important;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        padding-bottom: 0 !important;
    }

    /* Inactive tabs */
    .stTabs [data-baseweb="tab"] {
        background: #e8f1fb !important;
        color: #1e3a5f !important;
        border-radius: 12px 12px 0 0 !important;
        padding: clamp(9px, 1vw, 13px) clamp(10px, 1vw, 16px) !important;
        font-weight: 800 !important;
        white-space: nowrap !important;
        min-width: fit-content !important;
        border: 1px solid #c7d8ea !important;
        border-bottom: none !important;
    }

    /* Inactive tab text */
    .stTabs [data-baseweb="tab"] p {
        color: #1e3a5f !important;
        font-size: clamp(14px, 0.95vw, 17px) !important;
        font-weight: 800 !important;
        margin: 0 !important;
        line-height: 1.35 !important;
    }

    /* Active selected tab */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #16a34a 0%, #0f766e 100%) !important;
        color: white !important;
        border: 1px solid #0f766e !important;
        border-bottom: 3px solid #0f766e !important;
    }

    /* Active selected tab text */
    .stTabs [aria-selected="true"] p {
        color: white !important;
    }

    /* Hover tab */
    .stTabs [data-baseweb="tab"]:hover {
        background: #dbeafe !important;
        color: #1d4ed8 !important;
    }

    .stTabs [data-baseweb="tab"]:hover p {
        color: #1d4ed8 !important;
    }

    /* Keep active hover white */
    .stTabs [aria-selected="true"]:hover {
        background: linear-gradient(135deg, #15803d 0%, #0f766e 100%) !important;
    }

    .stTabs [aria-selected="true"]:hover p {
        color: white !important;
    }


    /* Responsive captions */
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {
        font-size: clamp(14px, 1vw, 17px) !important;
        color: #475569 !important;
        line-height: 1.65 !important;
        font-weight: 500 !important;
    }

    /* Responsive markdown/report text inside tabs */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        font-size: clamp(15px, 1vw, 17px) !important;
        line-height: 1.75 !important;
    }

    [data-testid="stMarkdownContainer"] h1 {
        font-size: clamp(28px, 3vw, 36px) !important;
        line-height: 1.2 !important;
    }

    [data-testid="stMarkdownContainer"] h2 {
        font-size: clamp(24px, 2.4vw, 30px) !important;
        line-height: 1.25 !important;
    }

    [data-testid="stMarkdownContainer"] h3 {
        font-size: clamp(21px, 2vw, 25px) !important;
        line-height: 1.3 !important;
    }

    @media (max-width: 720px) {
        .block-container {
            max-width: 96vw !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }

        .hero-title {
            letter-spacing: -0.035em;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 4px !important;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 9px 8px !important;
        }

        .score-card,
        .mini-card,
        .workflow-card,
        .section-box,
        .risk-box {
            border-radius: 16px !important;
        }
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
    language_display = st.selectbox("Language / Lingua", ["English", "Italian"], index=0)
    language = language_display
    T = UI_TEXT[language]

    st.header(T["sidebar_title"])
    st.write(T["sidebar_subtitle"])

    demo_display_names = display_options(list(DEMO_SCENARIOS.keys()), language)
    selected_demo_display = st.selectbox(T["demo_label"], demo_display_names)
    selected_demo = reverse_tr(selected_demo_display, language)
    demo = translated_demo_values(selected_demo, language)

    st.markdown(f"### {T['agent_status']}")
    status = featherless_status()
    if status == "Connected":
        st.success(T["connected"])
    elif status == "Disabled":
        st.warning(T["disabled"])
    else:
        st.warning(T["missing_key"])

    st.markdown(f"### {T['agent_stack']}")
    for item in T["stack_items"]:
        st.write(f"- {item}")

    st.info(T["demo_tip"])

st.markdown(
    f"""
    <div class="hero-box">
        <div class="hero-title">{T["hero_title"]}</div>
        <div class="hero-subtitle">{T["hero_subtitle"]}</div>
        <div class="badge-row">
            {''.join(f'<span class="badge">{badge}</span>' for badge in T["badges"])}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

workflow_cols = st.columns(4)
for col, (title, body) in zip(workflow_cols, T["workflow"]):
    with col:
        st.markdown(
            f'<div class="workflow-card"><b>{title}</b><br>{body}</div>',
            unsafe_allow_html=True,
        )

st.divider()

st.markdown(f"### {T['input_title']}")
st.caption(T["input_caption"])

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        product_name = st.text_input(T["product_name"], value=demo["product_name"])
        description = st.text_area(T["description"], value=demo["description"], height=105)
        raw_ingredients = st.text_area(T["ingredients"], value=demo["ingredients"], height=105)
        target_price = st.number_input(T["target_price"], min_value=1.0, max_value=100.0, value=float(demo["target_price"]), step=0.5)

    with col2:
        business_display_options = display_options(BUSINESS_TYPES, language)
        business_type_display = st.selectbox(
            T["business_type"],
            business_display_options,
            index=option_index(BUSINESS_TYPES, demo["business_type"]),
        )
        business_type = reverse_tr(business_type_display, language)

        location = st.text_input(T["location"], value=demo["location"])

        customer_display_options = display_options(CUSTOMER_SEGMENTS, language)
        customer_segment_display = st.selectbox(
            T["customer_segment"],
            customer_display_options,
            index=option_index(CUSTOMER_SEGMENTS, demo["customer_segment"]),
        )
        customer_segment = reverse_tr(customer_segment_display, language)

        dietary_display_options = display_options(DIETARY_FOCUS, language)
        dietary_focus_display = st.selectbox(
            T["dietary_focus"],
            dietary_display_options,
            index=option_index(DIETARY_FOCUS, demo["dietary_focus"]),
        )
        dietary_focus = reverse_tr(dietary_focus_display, language)

        complexity_options = ["Low", "Medium", "High"]
        complexity_display_options = display_options(complexity_options, language)
        preparation_complexity_display = st.selectbox(
            T["complexity"],
            complexity_display_options,
            index=option_index(complexity_options, demo["complexity"]),
        )
        preparation_complexity = reverse_tr(preparation_complexity_display, language)



run_clicked = st.button(T["run"], type="primary")

if run_clicked:
    ingredients = clean_ingredients(raw_ingredients)

    if not ingredients:
        st.error(T["validation_ingredients"])
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
        st.error(T["validation_input"])
        st.code(str(exc))
        st.stop()

    with st.spinner("Running MenuTaste reasoning workflow..." if language == "English" else "Esecuzione del workflow MenuTaste..."):
        report = run_menutaste_agent(product)

    st.markdown(f'<div class="success-box">{T["report_generated"]}</div>', unsafe_allow_html=True)

    score_values = [
        report.scores.overall_score,
        report.scores.nutrition_score,
        report.scores.quality_score,
        report.scores.market_fit_score,
        report.scores.operational_score,
    ]

    score_cols = st.columns(5)
    for col, label, value in zip(score_cols, T["scores"], score_values):
        with col:
            render_score_card(label, value, language)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(T["tabs"])

    with tab1:
        st.subheader(T["summary_title"])
        render_info_card(T["summary_card"], report.executive_summary)

        st.subheader(T["positioning_title"])
        render_info_card(T["positioning_card"], report.positioning)

        c1, c2, c3 = st.columns(3)
        with c1:
            render_small_card(T["business_type_card"], localized_value(report.product.business_type, language))
        with c2:
            render_small_card(T["target_customer_card"], localized_value(report.product.customer_segment, language))
        with c3:
            render_small_card(T["target_price_card"], f"EUR {report.product.target_price_eur:.2f}")

    with tab2:
        st.subheader(T["nutrition_title"])

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
                render_small_card(localized_value(label, language), localized_value(value, language))

        st.subheader(T["risk_title"])
        risk_values = [
            ", ".join(report.risks.allergen_risks),
            ", ".join(report.risks.dietary_conflicts),
            ", ".join(report.risks.quality_risks),
            ", ".join(report.risks.operational_risks),
        ]
        for label, value in zip(T["risk_labels"], risk_values):
            st.markdown(
                f"""
                <div class="risk-box">
                    <b>{label}</b><br>{value}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.subheader(T["ingredient_notes"])
        for ingredient, note in report.ingredient_notes.items():
            render_info_card(ingredient.title(), note)

    with tab3:
        st.subheader(T["ai_title"])
        st.caption(T["ai_caption"])
        st.markdown(report.ai_reasoning)

    with tab4:
        st.subheader(T["actions_title"])
        for idx, rec in enumerate(report.recommendations, start=1):
            render_info_card(f"{T['action']} {idx}", rec)

        st.subheader(T["checklist_title"])
        for idx, item in enumerate(report.launch_checklist):
            st.checkbox(item, value=False, key=f"launch_{idx}_{item}")

    with tab5:
        markdown_report = report_to_markdown(report)
        json_report = report_to_json(report)

        st.subheader(T["export_title"])
        e1, e2 = st.columns(2)
        with e1:
            st.download_button(
                T["download_md"],
                markdown_report,
                file_name="menutaste_report.md",
                mime="text/markdown",
            )
        with e2:
            st.download_button(
                T["download_json"],
                json_report,
                file_name="menutaste_report.json",
                mime="application/json",
            )

        st.subheader(T["markdown_preview"])
        st.text_area(T["report_content"], markdown_report, height=420, label_visibility="collapsed")
else:
    st.markdown(
        f"""
        <div class="section-box">
            <b>{T["ready_title"]}</b><br>
            {T["ready_body"]}
        </div>
        """,
        unsafe_allow_html=True,
    )
