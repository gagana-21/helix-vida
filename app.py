import os
from datetime import date

import pandas as pd
import streamlit as st

DATA_FILE = "patients.csv"  # single source of truth for the file name

# page config
st.set_page_config(
    page_title="VCU | We See You",
    page_icon="🩹",
    layout="centered",
)

# homepage
st.title("🏥 VCU")
st.subheader("Virtual Care Unit")
st.write("With you, throughout your recovery journey...")
st.warning("Prototype with synthetic data only. Not clinically validated and not a substitute for a doctor.")
st.divider()

st.header("Patient Info")
st.write("Enter patient details to begin with recovery monitoring")

# patient intake form
with st.form("patient_intake"):
    st.subheader("Basic Information")
    patient_id = st.text_input("Patient ID", placeholder="Example: VCU0001")
    patient_name = st.text_input("Patient Name", placeholder="Enter the name")
    age = st.number_input("Age", min_value=1, max_value=110, value=25)
    diabetes_type = st.selectbox(
        "Diabetes Type",
        ["Type 1", "Type 2", "Gestational", "Other/not specified"],
    )
    st.divider()
    st.subheader("Hospitalisation Details")
    discharge_date = st.date_input("Date of Discharge", value=date.today())
    hospital_name = st.text_input("Hospital name", placeholder="Enter name")
    recovery_notes = st.text_area(
        "Recovery notes", placeholder="Enter recovery / discharge notes"
    )
    submitted = st.form_submit_button("Register Patient")

# form checking
if submitted:
    if not patient_id.strip():
        st.error("Please enter a patient ID.")
    elif not patient_name.strip():
        st.error("Please enter patient name.")
    elif discharge_date > date.today():
        st.error("Discharge date is in the future!")
    else:
        # saving patient info
        patient_data = {
            "Patient ID": patient_id.strip(),
            "Patient Name": patient_name.strip(),
            "Age": age,
            "Diabetes Type": diabetes_type,
            "Discharge Date": discharge_date,
            "Hospital": hospital_name.strip(),
            "Recovery notes": recovery_notes.strip(),
        }
        new_patient = pd.DataFrame([patient_data])

        if os.path.exists(DATA_FILE):
            # dtype=str keeps IDs like "0001" intact
            existing_data = pd.read_csv(DATA_FILE, dtype=str)
            if patient_id.strip() in existing_data["Patient ID"].values:
                st.error("ID already exists!")
            else:
                updated_data = pd.concat(
                    [existing_data, new_patient], ignore_index=True
                )
                updated_data.to_csv(DATA_FILE, index=False)
                st.success("Patient registered successfully")
        else:
            new_patient.to_csv(DATA_FILE, index=False)
            st.success("Patient registered successfully")

# view registered patients
st.divider()
st.header("Registered Patients")
if os.path.exists(DATA_FILE):
    patient_records = pd.read_csv(DATA_FILE, dtype=str)
    st.dataframe(patient_records)
else:
    st.info("No patients have been registered yet")

# recovery plan generator
st.divider()
st.title("Recovery plan")
st.write("Structured recovery plan using patient data")

if not os.path.exists(DATA_FILE):
    st.warning("Please complete registering a patient first")
else:
    patient_records = pd.read_csv(DATA_FILE, dtype=str)

    if patient_records.empty:
        st.warning("No patient records available. Register a patient first")
    else:
        st.subheader("Select Patient")
        patient_ids = patient_records["Patient ID"].tolist()
        selected_patient_id = st.selectbox("Choose a registered patient", patient_ids)
        selected_patient = patient_records[
            patient_records["Patient ID"] == selected_patient_id
        ].iloc[0]

        # displaying patient details
        st.write("### Patient Information")
        st.write("**Name:**", selected_patient["Patient Name"])
        st.write("**Age:**", selected_patient["Age"])
        st.write("**Diabetes Type:**", selected_patient["Diabetes Type"])
        st.write("**Discharge Date:**", selected_patient["Discharge Date"])
        st.divider()

        # collect information from discharge documents
        st.subheader("Discharge Instructions")
        st.info("Information provided by the patient's healthcare team only*")

        with st.form("recovery_plan_form"):
            provider_name = st.text_input("Healthcare provider")
            followup_date = st.date_input(
                "Scheduled follow-up date", value=date.today()
            )
            medication_instructions = st.text_area(
                "Medication instructions",
                placeholder="Enter instructions from the discharge documents",
            )
            glucose_instructions = st.text_area(
                "Blood glucose monitoring instructions",
                placeholder="Enter the prescribed monitoring schedule",
            )
            meal_instruction = st.text_area(
                "Meal plan instruction",
                placeholder="Enter clinician provided dietary plan",
            )
            hypoglycemia_instructions = st.text_area(
                "Instructions for low blood glucose",
                placeholder="Enter the instructions provided by the medical practitioner",
            )
            st.subheader("Care co-ordination checklist")
            medication_reviewed = st.checkbox(
                "Medication list reviewed by healthcare team"
            )
            supplies_available = st.checkbox(
                "Required medications and monitoring supplies confirmed"
            )
            discharge_summary_shared = st.checkbox(
                "Discharge summary shared with the care team"
            )
            education_reviewed = st.checkbox("Patient education reviewed")
            generate_plan = st.form_submit_button("Generate Recovery Plan")

        # recovery plan
        if generate_plan:
            if followup_date < date.today():
                st.error("Please enter a valid upcoming follow-up date")
            else:
                recovery_plan = f"""
VCU - WE SEE YOU
PATIENT RECOVERY PLAN

PATIENT DETAILS

Patient ID: {selected_patient_id}
Patient Name: {selected_patient['Patient Name']}
Age: {selected_patient['Age']}
Diabetes Type: {selected_patient['Diabetes Type']}
Discharge Date: {selected_patient['Discharge Date']}

FOLLOW-UP INFORMATION

Healthcare Provider: {provider_name or 'Not provided'}
Follow-up Date: {followup_date}

MEDICATION INSTRUCTION

{medication_instructions or 'Not provided, confirm with healthcare team'}

GLUCOSE MONITORING

{glucose_instructions or 'Not provided, confirm with healthcare team'}

MEAL PLAN

{meal_instruction or 'Not provided, confirm with healthcare team'}

LOW BLOOD GLUCOSE INSTRUCTIONS

{hypoglycemia_instructions or 'Not provided, confirm with healthcare team'}

CARE CO-ORDINATION CHECKLIST

Medication reviewed: {'Yes' if medication_reviewed else 'Not confirmed'}
Supplies available: {'Yes' if supplies_available else 'Not confirmed'}
Discharge summary shared: {'Yes' if discharge_summary_shared else 'Not confirmed'}
Education needs reviewed: {'Yes' if education_reviewed else 'Not confirmed'}

IMPORTANT NOTICE

This document organises information provided by the healthcare team. It is not a prescription or a substitute for professional medical advice.
Any missing instructions must be confirmed with the patient's healthcare team.
"""
                # keep the plan across reruns (clicking Download triggers a rerun)
                st.session_state["recovery_plan"] = recovery_plan
                st.session_state["recovery_plan_id"] = selected_patient_id

        if (
            "recovery_plan" in st.session_state
            and st.session_state.get("recovery_plan_id") == selected_patient_id
        ):
            st.success("Recovery plan generated!")
            st.subheader("Generated recovery plan")
            st.text(st.session_state["recovery_plan"])

            # allow the user to download the plan
            st.download_button(
                label="Download Recovery Plan",
                data=st.session_state["recovery_plan"],
                file_name=f"{selected_patient_id}_recovery_plan.txt",
                mime="text/plain",
            )
