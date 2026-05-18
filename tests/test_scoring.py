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
    scores = calculate_scores(["chickpeas", "spinach", "olive oil"], 8.0, "High protein", "Medium")
    assert 0 <= scores["overall_score"] <= 100
