# Architecture

MenuTaste follows a simple production-style architecture.

## Components

1. Streamlit Web UI
   - Collects food product details.
   - Displays scorecards, reasoning, risks, recommendations, and exports.

2. Validation Layer
   - Cleans ingredient input.
   - Validates structured product data with Pydantic.

3. Deterministic Analysis Engine
   - Estimates nutrition signals from ingredient hints.
   - Detects allergens and dietary conflicts.
   - Scores nutrition, quality, market fit, and operations.

4. Featherless Reasoning Layer
   - Uses OpenAI-compatible Featherless chat completions.
   - Produces strategic product reasoning.
   - Falls back safely if the API key is missing.

5. Report Layer
   - Creates Markdown and JSON exports.

## Why This Is Agentic

The app does not only chat. It follows a multi-step workflow:

Input -> validation -> nutrition analysis -> risk detection -> scoring -> AI reasoning -> recommendations -> launch checklist -> export.
