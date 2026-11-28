import pandas as pd
import streamlit as st

from src.alerts import LEVEL_ORDER, load_rules, patient_status
from src.storage import load_checkins, load_patients

st.set_page_config(page_title="Navigator Dashboard | VCU", page_icon="🧭", layout="wide")
st.title("🧭 Navigator Dashboard")
st.warning("Prototype with synthetic data only. Not clinically validated, not medical advice.")

rules = load_rules()
if not rules.get("reviewed_by_clinician", False):
    st.caption("⚠️ Alert rules have not been clinically reviewed yet.")

patients = load_patients()
checkins = load_checkins()
if patients.empty:
    st.info("No patients yet. Register one on the main page or run make_synthetic.py.")
    st.stop()

LABEL = {"green": "🟢 Green", "amber": "🟠 Amber", "red": "🔴 Red"}

rows = []
for _, p in patients.iterrows():
    s = patient_status(p, checkins, rules)
    rows.append({
        "Patient ID": p["Patient ID"],
        "Name": p["Patient Name"],
        "Status": LABEL[s["status"]],
        "Last check-in": s["last_checkin"],
        "Days since": s["days_since"],
        "Why flagged": "; ".join(s["reasons"]),
        "_level": s["status"],
    })

df = pd.DataFrame(rows)
df["_order"] = df["_level"].map(LEVEL_ORDER)
df = df.sort_values(["_order", "Days since"], ascending=[False, False])

c1, c2, c3 = st.columns(3)
c1.metric("🔴 Red", int((df["_level"] == "red").sum()))
c2.metric("🟠 Amber", int((df["_level"] == "amber").sum()))
c3.metric("🟢 Green", int((df["_level"] == "green").sum()))

show = ["Patient ID", "Name", "Status", "Last check-in", "Days since", "Why flagged"]

st.subheader("Needs review")
queue = df[df["_level"] != "green"]
if queue.empty:
    st.success("Nobody needs review right now.")
else:
    st.dataframe(queue[show], hide_index=True)

st.subheader("All patients")
choice = st.selectbox("Filter", ["All", "Red", "Amber", "Green"])
view = df if choice == "All" else df[df["_level"] == choice.lower()]
st.dataframe(view[show], hide_index=True)
