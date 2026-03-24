from app.domain.curriculum.linker import CurriculumLinker, CurriculumNode


def test_builds_requested_relationship_types():
    nodes = [
        CurriculumNode(
            id="ov-1",
            node_type="overview_block",
            title="Year 4 multiplication and division",
            text="Understand multiplication facts and division relationships.",
            year="year4",
            strand="multiplication_division",
        ),
        CurriculumNode(
            id="prog-1",
            node_type="progression_statement",
            text="Use multiplication facts to derive related division facts.",
            year="year4",
            strand="multiplication_division",
        ),
        CurriculumNode(
            id="vocab-1",
            node_type="vocabulary_expectation",
            text="fact family product quotient",
            year="year4",
            strand="multiplication_division",
        ),
        CurriculumNode(
            id="policy-1",
            node_type="calculation_policy_method",
            title="Year 4 short multiplication",
            text="Short multiplication method for multiplying a 2-digit by 1-digit number.",
            year="year4",
            strand="multiplication_division",
        ),
        CurriculumNode(
            id="focus-1",
            node_type="times_table_focus",
            title="Year 4 tables",
            text="Secure 6, 7, 8, 9 and 12 times tables.",
            year="year4",
            strand="multiplication_division",
        ),
        CurriculumNode(
            id="obj-1",
            node_type="multiplication_division_objective",
            text="Recall multiplication and division facts for tables up to 12 x 12.",
            year="year4",
            strand="multiplication_division",
        ),
    ]

    linker = CurriculumLinker()
    links = linker.build_links(nodes)

    relations = {link.relation for link in links}
    assert "overview_to_progression" in relations
    assert "progression_to_vocabulary" in relations
    assert "policy_method_to_block" in relations
    assert "times_table_to_objective" in relations


def test_lesson_planner_context_chains_progression_to_vocab():
    nodes = [
        CurriculumNode(
            id="ov-1",
            node_type="overview_block",
            text="fractions and decimals",
        ),
        CurriculumNode(
            id="prog-1",
            node_type="progression_statement",
            text="compare and order decimal numbers",
        ),
        CurriculumNode(
            id="vocab-1",
            node_type="vocabulary_expectation",
            text="decimal place value",
        ),
    ]

    linker = CurriculumLinker()
    linker.build_links(nodes)

    context = linker.lesson_planner_context("ov-1")
    assert context["progression_statement_ids"] == ["prog-1"]
    assert context["vocabulary_expectation_ids"] == ["vocab-1"]
