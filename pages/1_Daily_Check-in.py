from datetime import date

import streamlit as st

from src.alerts import evaluate_checkin, load_rules
from src.storage import get_consent, load_patients, save_checkin, set_consent

st.set_page_config(page_title="Daily Check-in | VCU", page_icon="📝")
st.title("📝 Daily Check-in")
st.warning("Prototype - not medical advice. If you feel very unwell, contact your doctor "
           "or call your local emergency number (112 in India) straight away.")

patients = load_patients()
if patients.empty:
    st.info("Register a patient on the main page first.")
    st.stop()

rules = load_rules()
symptom_options = [r["symptom"] for r in rules["rules"] if r["type"] == "symptom"]

patient_id = st.selectbox("Patient ID", patients["Patient ID"].tolist())

# consent toggle (patient-controlled, off by default)
current = get_consent(patient_id)
consent = st.toggle("Let my caregiver see a summary of my recovery", value=current,
                    key=f"consent_{patient_id}")
if consent != current:
    set_consent(patient_id, consent)
    st.toast("Sharing preference saved")

st.divider()

with st.form("checkin_form"):
    measured = st.checkbox("I measured my blood glucose today", value=True)
    glucose = st.number_input("Blood glucose (mg/dL)", min_value=20, max_value=600, value=110)
    took = st.radio("Did you take your medicines as prescribed?",
                    ["Yes", "Partly", "No"], horizontal=True)
    symptoms = st.multiselect("Do you have any of these today?", symptom_options)
    submitted = st.form_submit_button("Submit check-in")

if submitted:
    checkin = {
        "glucose": glucose if measured else None,
        "took_medicines": took,
        "symptoms": symptoms,
    }
    status, triggered = evaluate_checkin(checkin, rules)
    save_checkin({
        "Patient ID": patient_id,
        "Date": date.today().isoformat(),
        "Glucose": glucose if measured else "",
        "Took medicines": took,
        "Symptoms": "; ".join(symptoms),
        "Status": status,
        "Reasons": " | ".join(r["message"] for r in triggered),
    })

    # The patient only sees a neutral message: no diagnosis, no medical advice.
    if status == "red":
        st.error("Thank you. Your care navigator has been alerted and will contact you soon. "
                 "If you feel very unwell, call your doctor or emergency number now.")
    elif status == "amber":
        st.warning("Thank you. Your care team will keep a closer eye on your recovery.")
    else:
        st.success("Thank you. Your check-in has been recorded.")
