import csv

import pytest

from src.alerts import evaluate_checkin, load_rules, missed_checkin_level

RULES = load_rules()
SYMPTOM_TEXT = {r["id"]: r["symptom"] for r in RULES["rules"] if r["type"] == "symptom"}


def load_cases():
    with open("tests/gold_cases.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.mark.parametrize("case", load_cases(), ids=lambda c: c["case_id"])
def test_gold_case(case):
    checkin = {
        "glucose": float(case["glucose"]) if case["glucose"] else None,
        "took_medicines": case["took_medicines"],
        "symptoms": [SYMPTOM_TEXT[s] for s in case["symptom_ids"].split(";") if s],
    }
    status, _ = evaluate_checkin(checkin, RULES)
    assert status == case["expected_status"]


def test_missed_checkins():
    assert missed_checkin_level(0, RULES) == "green"
    assert missed_checkin_level(2, RULES) == "amber"
    assert missed_checkin_level(4, RULES) == "red"
