import streamlit as st
from datetime import date
from supabase import create_client
from db import add_client
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

new_client_toggle = st.checkbox("➕ Add a new client instead of selecting existing")

if new_client_toggle:
    with st.form("inline_add_client"):
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        address = st.text_input("Home Address")
        rooms = st.text_input("Room(s) of Interest")
        style = st.text_input("Style Preference")
        budget = st.text_input("Estimated Budget")
        save_client = st.form_submit_button("Save New Client")

        if save_client:
            if not name.strip():
                st.warning("Name is required.")
            elif not (phone.strip() or email.strip() or address.strip()):
                st.warning("At least one contact method (phone, email, or address) is required.")
            else:
                add_client(name, phone, email, address, rooms, style, budget)
                st.success("Client added!")

                # Refresh client list & auto-select new client
                st.session_state["selected_client_name"] = name
                st.rerun()
else:
    selected_client_name = st.selectbox("Select Client", ["-- Select Client --"] + list(client_options.keys()), key="selected_client_name")
    if selected_client_name != "-- Select Client --":
        selected_client_id = client_options[selected_client_name]

# -------------------------------
# Sale Entry Form
# -------------------------------
with st.form("record_sale_form"):
    st.subheader("💼 Sale Details")

    sale_date = st.date_input("Sale Date", value=date.today())
    amount = st.number_input("Sale Amount", min_value=0.0, step=50.0, format="%.2f")
    status = st.selectbox("Sale Status", ["Unsold", "Open", "Closed", "Void"])
    notes = st.text_area("Notes (optional)")

    submitted = st.form_submit_button("Record Sale")

    if submitted:
        if client_data == "-- Select Client --":
            st.warning("Please select a client.")
        elif amount <= 0:
            st.warning("Please enter a valid sale amount.")
        else:
            supabase.table("sales").insert({
                "client_id": client_options[client_data],
                "date": sale_date.isoformat(),
                "amount": amount,
                "status": status,
                "notes": notes
            }).execute()
            st.success("Sale recorded successfully!")
