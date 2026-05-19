# Vultr Deployment Guide

## Project

MenuTaste AI Agent

## Goal

Deploy a web-based AI food product analysis agent on Vultr using Streamlit and Featherless AI.

## Required environment variables

```env
USE_FEATHERLESS=true
FEATHERLESS_API_KEY=your_featherless_api_key_here
FEATHERLESS_BASE_URL=https://api.featherless.ai/v1
FEATHERLESS_MODEL=Qwen/Qwen2.5-7B-Instruct
```

## Local run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Docker run

```bash
docker build -t menutaste-ai-agent .
docker run -p 8501:8501 --env-file .env menutaste-ai-agent
```

Then open:

```text
http://YOUR_VULTR_SERVER_IP:8501
```

## Production Notes

- Use a domain name for the final demo URL if available.
- Use HTTPS if time allows.
- Do not commit `.env`.
- Keep the Featherless API key private.
- Commit `.env.example` so reviewers know which variables are required.