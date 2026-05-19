from src.menutaste.scoring import detect_allergens, estimate_nutrition, calculate_scores


def test_detect_allergens():
    allergens = detect_allergens(["milk", "wheat bread", "tomato"])
    assert "dairy" in allergens
    assert "gluten" in allergens


def test_estimate_nutrition_high_protein():
    result = estimate_nutrition(["chickpeas", "lentils", "spinach"])
    assert result["protein_level"] == "High"
    assert result["fiber_signal"] in {"Medium", "High"}


def test_calculate_scores_bounds():
    scores = calculate_scores(
        ["chickpeas", "spinach", "olive oil"],
        8.0,
        "High protein",
        "Medium",
        business_type="Cafe",
        customer_segment="Office workers",
        location="Milan, Italy",
        description="A healthy breakfast bowl",
    )
    assert 0 <= scores["overall_score"] <= 100


def test_calculate_scores_responds_to_market_inputs():
    base_scores = calculate_scores(
        ["chickpeas", "spinach", "olive oil"],
        8.0,
        "High protein",
        "Medium",
        business_type="Cafe",
        customer_segment="Office workers",
        location="Milan, Italy",
        description="A healthy breakfast bowl",
    )
    changed_scores = calculate_scores(
        ["chickpeas", "spinach", "olive oil"],
        14.0,
        "High protein",
        "High",
        business_type="Food truck",
        customer_segment="Students",
        location="Small town",
        description="A simple bowl",
    )

    assert base_scores["market_fit_score"] != changed_scores["market_fit_score"]
    assert base_scores["operational_score"] != changed_scores["operational_score"]
    assert base_scores["overall_score"] != changed_scores["overall_score"]
