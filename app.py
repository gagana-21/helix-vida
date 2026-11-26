import streamlit as st
import pandas as pd
import os
from datetime import date 

#page config
st.set_page_config(
    page_title="VCU | We See You",
    page_icon="🩹",
    layout="centered"
)

#homepage
st.title("🏥VCU")
st.subheader("Virtual Care Unit")
st.write("With you, throughout your recovery journey...")
st.divider()

st.header("Patient Info")
st.write("Enter patient details to begin with recovery monitoring")

#patient intake form
with st.form("patient_intake"):
    st.subheader("Basic Information")
    patient_id = st.text_input(
        "Patient ID",
        placeholder="Example: VCU0001"
    )
    patient_name = st.text_input(
        "Patient Name",
        placeholder="Enter the name"
    )
    age = st.number_input(
        "Age",
        min_value=1,
        max_value=110,
        value=25
    )
    diabetes_type = st.selectbox(
        "Diabetes Type",
        ["Type 1", "Type 2", "Gestational", "Other/not specified"]
    )
    st.divider()
    st.subheader("Hospitalisation Details")
    discharge_date = st.date_input(
        "Date of Discharge",
        value = date.today()
    )
    hospital_name = st.text_input(
        "Hospital name",
        placeholder="Enter name"
    )
    recovery_notes = st.text_area(
        "Recovery notes",
        placeholder="Enter delivery information"
    )
    submitted = st.form_submit_button(
        "Register Patient"
    )

#form checking
if submitted:
    if not patient_id.strip():
        st.error("Please enter a patient ID...")
    elif not patient_name.strip():
        st.error("Please enter patient name....")
    elif discharge_date > date.today():
        st.error("Discharge date is in the future!!")
    else:

        #saving patient info
        patient_data = {
            "Patient ID": patient_id.strip(),
            "Patient name": patient_name.strip(),
            "Age": age,
            "Diabetes Type": diabetes_type,
            "Discharge Date": discharge_date,
            "Hospital": hospital_name.strip(),
            "Recovery notes": recovery_notes.strip()
        }
        new_patient = pd.DataFrame([patient_data])
        file_name = "patient.csv"
        if os.path.exists(file_name):
            existing_data = pd.read_csv(file_name)
            if patient_id.strip() in existing_data["Patient ID"].astype(str).values:
                st.error("ID already exists!!")
            else:
                updated_data = pd.concat(
                    [existing_data, new_patient],
                    ignore_index=True
                )
                updated_data.to_csv(
                    file_name,
                    index=False
                )
                st.success("Patient registered successfully")
        else:
            new_patient.to_csv(
                file_name,
                index=False
            )
            st.success("Patient registered successfully")

#view registered patients

st.divider()
st.header("Registered Patients")
if os.path.exists("patients.csv"):
    patient_records = pd.read_csv("patients.csv")
    st.dataframe(
        patient_records,
        use_container_width=True
    )
else:
    st.info("No patients have been registered yet")    
