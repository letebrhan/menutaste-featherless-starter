from src.menutaste.agent import run_menutaste_agent
from src.menutaste.models import ProductInput


def test_run_menutaste_agent_without_api_key(monkeypatch):
    monkeypatch.delenv("FEATHERLESS_API_KEY", raising=False)

    product = ProductInput(
        product_name="Test bowl",
        description="A chickpea and spinach bowl",
        ingredients=["chickpeas", "spinach", "olive oil"],
        business_type="Cafe",
        location="Milan",
        customer_segment="Office workers",
        dietary_focus="High protein",
        target_price_eur=8.5,
        preparation_complexity="Medium",
    )
    report = run_menutaste_agent(product)
    assert report.scores.overall_score > 0
    assert "Featherless is not configured" in report.ai_reasoning
