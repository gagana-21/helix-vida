"""Creates 30 SYNTHETIC patients and their check-ins. Seeded, so results are reproducible.
Run:  python make_synthetic.py      (safe to re-run; only rows with IDs starting 'SYN' are replaced)"""
import os
import random
from datetime import date, timedelta

import pandas as pd

from src.alerts import evaluate_checkin, load_rules
from src.storage import CHECKINS_FILE, CHECKIN_COLUMNS, CONSENT_FILE, PATIENTS_FILE

random.seed(42)
TODAY = date.today()
rules = load_rules()
SYMPTOM = {r["id"]: r["symptom"] for r in rules["rules"] if r["type"] == "symptom"}

FIRST = ["Asha", "Ravi", "Meena", "Kiran", "Suresh", "Lakshmi", "Arjun", "Divya",
         "Mohan", "Priya", "Rahul", "Sunita", "Vikram", "Anita", "Girish"]
LAST = ["K.", "R.", "S.", "N.", "M.", "P."]
PATTERNS = ["steady"] * 14 + ["missed"] * 5 + ["lows"] * 4 + ["skips"] * 4 + ["wound"] * 3


def one_checkin(pattern, days_ago):
    glucose = random.randint(90, 160)
    took = "Yes"
    symptoms = []
    recent = days_ago <= 1
    if pattern == "lows" and recent:
        glucose = random.randint(48, 66)
    if pattern == "skips" and recent:
        took = random.choice(["No", "Partly"])
    if pattern == "wound" and recent:
        symptoms = [SYMPTOM["S5"]]
        if random.random() < 0.5:
            symptoms.append(SYMPTOM["S4"])
    return glucose, took, symptoms


def merge_and_save(path, new_df):
    if os.path.exists(path):
        old = pd.read_csv(path, dtype=str)
        old = old[~old["Patient ID"].str.startswith("SYN")]
        new_df = pd.concat([old, new_df], ignore_index=True)
    new_df.to_csv(path, index=False)


patients, checkins, consents = [], [], []
random.shuffle(PATTERNS)

for i, pattern in enumerate(PATTERNS, start=1):
    pid = f"SYN{i:03d}"
    n_days = random.randint(3, 8)
    discharge = TODAY - timedelta(days=n_days)
    patients.append({
        "Patient ID": pid,
        "Patient Name": f"{random.choice(FIRST)} {random.choice(LAST)} (synthetic)",
        "Age": random.randint(55, 85),
        "Diabetes Type": random.choice(["Type 2", "Type 2", "Type 1"]),
        "Discharge Date": discharge.isoformat(),
        "Hospital": "Synthetic Hospital",
        "Recovery notes": "Synthetic record for demo",
    })
    consents.append({"Patient ID": pid, "Consent": random.choice(["yes", "no"])})

    last_day = TODAY - timedelta(days=random.choice([2, 3, 4, 5])) if pattern == "missed" else TODAY
    for d in range(1, n_days + 1):
        day = discharge + timedelta(days=d)
        if day > last_day:
            continue
        glucose, took, symptoms = one_checkin(pattern, (TODAY - day).days)
        status, triggered = evaluate_checkin(
            {"glucose": glucose, "took_medicines": took, "symptoms": symptoms}, rules)
        checkins.append({
            "Patient ID": pid, "Date": day.isoformat(), "Glucose": glucose,
            "Took medicines": took, "Symptoms": "; ".join(symptoms),
            "Status": status, "Reasons": " | ".join(r["message"] for r in triggered),
        })

merge_and_save(PATIENTS_FILE, pd.DataFrame(patients))
merge_and_save(CHECKINS_FILE, pd.DataFrame(checkins, columns=CHECKIN_COLUMNS))
merge_and_save(CONSENT_FILE, pd.DataFrame(consents))
print(f"Created {len(patients)} synthetic patients and {len(checkins)} check-ins.")
