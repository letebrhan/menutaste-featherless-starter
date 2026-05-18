# MenuTaste AI Agent

MenuTaste is a web-based enterprise AI agent for food entrepreneurs, cafes, restaurants, caterers, cloud kitchens, and packaged food startups.

It analyzes a food or drink idea and generates a practical report covering:

- nutrition profile
- protein, carbohydrate, fat, sugar, salt, fiber, and vitamin signals
- ingredient quality notes
- allergen and dietary risks
- market positioning
- customer fit
- improvement recommendations
- launch checklist
- exportable Markdown and JSON reports

## Hackathon Positioning

This project is designed for the AI Agent Olympics Hackathon at Milan AI Week 2026.

It fits these tracks:

- Intelligent Reasoning: evaluates product quality, nutrition, business fit, and risks.
- Agentic Workflows: follows a multi-step workflow from input validation to scoring and final report generation.
- Enterprise Utility: helps food entrepreneurs make faster product decisions.
- Production-style Web App: includes Streamlit UI, modular Python code, tests, Docker, and Vultr deployment notes.
- Featherless Challenge Fit: domain-specialized, open-source, reproducible, and deployable.

## Featherless Integration

The app supports Featherless through an OpenAI-compatible client.

Default model:

```text
Qwen/Qwen2.5-7B-Instruct
```

You can change it in `.env`.

The app also has deterministic fallback logic, so it still works without an API key during local testing.

## Run Locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

## Required Environment Variables

```bash
FEATHERLESS_API_KEY=your_key_here
FEATHERLESS_MODEL=Qwen/Qwen2.5-7B-Instruct
FEATHERLESS_BASE_URL=https://api.featherless.ai/v1
USE_FEATHERLESS=true
```

## Run Tests

```bash
pytest -q
```

## Docker

```bash
docker build -t menutaste-featherless .
docker run --env-file .env -p 8501:8501 menutaste-featherless
```

Then open:

```text
http://localhost:8501
```

## Demo Story

A cafe owner, restaurant founder, or packaged food entrepreneur enters a food or drink idea. MenuTaste acts like a food product analyst. It checks the ingredients, estimates nutrition signals, detects risks, calls Featherless for business reasoning, and produces a launch-ready report.
