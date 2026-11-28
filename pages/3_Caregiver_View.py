import pandas as pd
import streamlit as st

from src.alerts import load_rules, patient_status
from src.storage import get_consent, load_checkins, load_patients

st.set_page_config(page_title="Caregiver View | VCU", page_icon="👪")
st.title("👪 Caregiver View")
st.warning("Prototype - not medical advice. A real version would need a secure login.")

patients = load_patients()
if patients.empty:
    st.info("No patients registered yet.")
    st.stop()

patient_id = st.selectbox("Patient ID", patients["Patient ID"].tolist())

if not get_consent(patient_id):
    st.info("This patient has not chosen to share their recovery summary. "
            "They can switch sharing on from their Daily Check-in page.")
    st.stop()

patient = patients[patients["Patient ID"] == patient_id].iloc[0]
checkins = load_checkins()
s = patient_status(patient, checkins, load_rules())

st.subheader(f"Recovery summary for {patient['Patient Name']}")
MESSAGE = {
    "green": ("success", "On track. Recent check-ins look as expected."),
    "amber": ("warning", "The care team is keeping a closer eye on the recovery."),
    "red": ("error", "The care navigator has been alerted and is following up."),
}
kind, text = MESSAGE[s["status"]]
getattr(st, kind)(text)

st.write("**Last check-in:**", s["last_checkin"])
st.write("**Days since last check-in:**", s["days_since"])

mine = checkins[checkins["Patient ID"] == patient_id].sort_values("Date", kind="stable")
if not mine.empty:
    chart = mine.tail(7).copy()
    chart["Glucose"] = pd.to_numeric(chart["Glucose"], errors="coerce")
    st.caption("Blood glucose from recent check-ins (mg/dL)")
    st.line_chart(chart.set_index("Date")["Glucose"])
