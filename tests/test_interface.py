from interface.main import build_demo_lesson_plan, home


def test_demo_lesson_plan_contains_expected_sections():
    response = build_demo_lesson_plan(
        year_group="Year 4",
        block="Multiplication and division",
        objective="Multiply a 2-digit number by 1-digit",
    )

    assert len(response.phases) == 3
    assert response.phases[0].cpa_stage == "concrete"
    assert response.phases[1].cpa_stage == "pictorial"
    assert response.phases[2].cpa_stage == "abstract"


def test_home_page_mentions_demo_endpoint():
    html = home()
    assert "Urban Fishstick — Minimal Interface" in html
    assert "/api/lesson-plan" in html
