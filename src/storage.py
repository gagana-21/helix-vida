"""All reading/writing of CSV files lives here, so pages stay simple."""
import os

import pandas as pd

PATIENTS_FILE = "patients.csv"
CHECKINS_FILE = "checkins.csv"
CONSENT_FILE = "consent.csv"

CHECKIN_COLUMNS = [
    "Patient ID", "Date", "Glucose", "Took medicines",
    "Symptoms", "Status", "Reasons",
]


def load_patients():
    if os.path.exists(PATIENTS_FILE):
        return pd.read_csv(PATIENTS_FILE, dtype=str).fillna("")
    return pd.DataFrame()


def load_checkins():
    if os.path.exists(CHECKINS_FILE):
        return pd.read_csv(CHECKINS_FILE, dtype=str).fillna("")
    return pd.DataFrame(columns=CHECKIN_COLUMNS)


def save_checkin(row: dict):
    df = pd.concat([load_checkins(), pd.DataFrame([row])], ignore_index=True)
    df.to_csv(CHECKINS_FILE, index=False)


def get_consent(patient_id: str) -> bool:
    if not os.path.exists(CONSENT_FILE):
        return False
    df = pd.read_csv(CONSENT_FILE, dtype=str)
    rows = df[df["Patient ID"] == patient_id]
    return (not rows.empty) and rows.iloc[-1]["Consent"] == "yes"


def set_consent(patient_id: str, value: bool):
    if os.path.exists(CONSENT_FILE):
        df = pd.read_csv(CONSENT_FILE, dtype=str)
        df = df[df["Patient ID"] != patient_id]
    else:
        df = pd.DataFrame(columns=["Patient ID", "Consent"])
    new_row = pd.DataFrame([{"Patient ID": patient_id,
                             "Consent": "yes" if value else "no"}])
    pd.concat([df, new_row], ignore_index=True).to_csv(CONSENT_FILE, index=False)
