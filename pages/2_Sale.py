import streamlit as st
from datetime import date
from supabase import create_client
import os

# Supabase init
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

st.set_page_config(page_title="Sale", page_icon="🧾")
st.title("🧾 Record a Sale")

# Fetch clients
client_data = supabase.table("clients").select("id", "name").order("name").execute()
clients = client_data.data

client_options = {client["name"]: client["id"] for client in clients}

# -------------------------------
# Sale Entry Form
# -------------------------------
with st.form("record_sale_form"):
    st.subheader("💼 Sale Details")

    client_name = st.selectbox("Select Client", ["-- Select Client --"] + list(client_options.keys()))
    sale_date = st.date_input("Sale Date", value=date.today())
    amount = st.number_input("Sale Amount", min_value=0.0, step=50.0, format="%.2f")
    status = st.selectbox("Sale Status", ["Unsold", "Open", "Closed", "Void"])
    notes = st.text_area("Notes (optional)")

    submitted = st.form_submit_button("Record Sale")

    if submitted:
        if client_name == "-- Select Client --":
            st.warning("Please select a client.")
        elif amount <= 0:
            st.warning("Please enter a valid sale amount.")
        else:
            supabase.table("sales").insert({
                "client_id": client_options[client_name],
                "date": sale_date.isoformat(),
                "amount": amount,
                "status": status,
                "notes": notes
            }).execute()
            st.success("Sale recorded successfully!")
