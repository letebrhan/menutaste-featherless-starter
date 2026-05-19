# MenuTaste Architecture

## Overview

MenuTaste is a Streamlit-based AI agent for food entrepreneurs. It analyzes a food or drink idea and generates a product-quality, nutrition, risk, market-fit, and launch-readiness report.

## Main Components

## 1. Streamlit UI

File: `app.py`

The UI collects:

- Product name
- Description
- Ingredients
- Business type
- Location
- Customer segments
- Dietary focuses
- Target price
- Preparation complexity
- Output language

## 2. Local Analysis Engine

Files:

- `src/menutaste/scoring.py`
- `src/menutaste/nutrition_db.py`
- `src/menutaste/validators.py`

The local engine performs deterministic checks for:

- Nutrition signals
- Allergen risks
- Dietary conflicts
- Market fit
- Operational complexity
- Overall score

## 3. Agent Workflow

File: `src/menutaste/agent.py`

The agent combines:

- Cleaned product input
- Nutrition estimate
- Risk assessment
- Score calculation
- Featherless AI reasoning
- Recommendations
- Launch checklist

## 4. Featherless AI Reasoning

File: `src/menutaste/llm_client.py`

The app sends a structured prompt to a Featherless-hosted open-source model. The model produces business-ready reasoning in English or Italian.

## 5. Export Layer

Files:

- `src/menutaste/report.py`
- `src/menutaste/export_utils.py`

The app exports reports as:

- Markdown
- JSON

## Data Flow

User input -> Validation -> Local scoring -> Featherless reasoning -> Agent report -> UI tabs -> Markdown/JSON export