"""Alert engine. It contains NO clinical numbers: everything comes from rules/conditions.json."""
import json
from datetime import date, datetime

LEVEL_ORDER = {"green": 0, "amber": 1, "red": 2}

OPS = {
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
}


def load_rules(path="rules/conditions.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def worst(levels):
    """Return the most serious level in a list (green if the list is empty)."""
    return max(levels, key=lambda lv: LEVEL_ORDER[lv], default="green")


def evaluate_checkin(checkin: dict, rules: dict):
    """
    checkin = {"glucose": 110 or None, "took_medicines": "Yes"/"Partly"/"No", "symptoms": [..]}
    Returns (status, list_of_triggered_rules).
    """
    triggered = []
    for rule in rules["rules"]:
        kind = rule["type"]
        if kind == "threshold":
            value = checkin.get(rule["field"])
            hit = value is not None and OPS[rule["op"]](value, rule["value"])
        elif kind == "choice":
            hit = checkin.get(rule["field"]) == rule["equals"]
        elif kind == "symptom":
            hit = rule["symptom"] in checkin.get("symptoms", [])
        else:
            hit = False
        if hit:
            triggered.append(rule)
    status = worst([r["level"] for r in triggered])
    return status, triggered


def missed_checkin_level(days_since_last: int, rules: dict):
    cfg = rules["missed_checkin_days"]
    if days_since_last >= cfg["red"]:
        return "red"
    if days_since_last >= cfg["amber"]:
        return "amber"
    return "green"


def _to_date(text):
    return datetime.strptime(str(text)[:10], "%Y-%m-%d").date()


def patient_status(patient, checkins, rules, today=None):
    """Overall status = worse of (latest check-in status, missed-check-in level)."""
    today = today or date.today()
    mine = checkins[checkins["Patient ID"] == patient["Patient ID"]]
    reasons = []

    if mine.empty:
        last_date = _to_date(patient["Discharge Date"])  # count from discharge
        last_status = "green"
        last_label = "None yet"
    else:
        last = mine.sort_values("Date", kind="stable").iloc[-1]
        last_date = _to_date(last["Date"])
        last_status = last["Status"] or "green"
        last_label = str(last_date)
        if last["Reasons"]:
            reasons.extend(last["Reasons"].split(" | "))

    days = (today - last_date).days
    missed = missed_checkin_level(days, rules)
    if missed != "green":
        reasons.append(f"No check-in for {days} days")

    return {
        "status": worst([last_status, missed]),
        "reasons": reasons,
        "days_since": days,
        "last_checkin": last_label,
    }
