def test_experiment_plan_has_reproducibility_fields():
    from app.services.experiments.planner import build_experiment_plan
    plan = build_experiment_plan(
        hypothesis="The intervention improves the primary metric.",
        gap={"gap_type": "missing_experiment"},
        evidence=[{"paper_id": 1}],
    )
    assert plan["result_status"] == "not_run"
    assert plan["baselines"]
    assert plan["metrics"]
    assert plan["ablations"]
    assert plan["protocol"]

def test_experiment_plan_does_not_claim_results():
    from app.services.experiments.planner import build_experiment_plan
    plan = build_experiment_plan(
        hypothesis="Testable hypothesis",
        gap={"gap_type": "underexplored_topic"},
    )
    assert plan["result_status"] == "not_run"
