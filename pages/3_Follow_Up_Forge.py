import streamlit as st
from datetime import date
from db import (
    get_all_clients_with_ids,
    get_client_by_id,
    get_room_sketches_by_client,
    add_note,
)
from ai_helper import generate_followup_from_template
import json

# Load templates
with open("templates/followups.json", "r") as f:
    followup_templates = json.load(f)

st.set_page_config(page_title="✉️ Follow-Up Forge", page_icon="✉️")
st.title("✉️ Follow-Up Forge")

# Select client
clients = get_all_clients_with_ids()
client_options = {f"{c['name']} ({c['phone']})": c["id"] for c in clients}
client_display = st.selectbox("Select Client", ["-- Select --"] + list(client_options.keys()))

if client_display != "-- Select --":
    selected_id = client_options[client_display]
    client_data = get_client_by_id(selected_id)
    sketches = get_room_sketches_by_client(selected_id)
    latest_sketch = sketches[-1] if sketches else {}

    # Select follow-up type
    guest_type = st.selectbox("Guest Type", ["bought", "browsed"])
    style = st.selectbox("Message Style", ["text", "phone", "email", "handwritten"])

    if st.button("📋 Generate AI Follow-Up"):
        # Load and format the selected template
        template = followup_templates.get(guest_type, {}).get(style)
        template_text = f"Subject: {template['subject']}\n\n{template['body']}" if isinstance(template, dict) else template

        # 🧠 Show spinner while AI is processing
        with st.spinner("Talking to the AI..."):
            ai_response = generate_followup_from_template(template_text, client_data, latest_sketch, message_style=style)

        st.markdown("### 🧠 AI-Generated Message")
        st.markdown(ai_response)

        # Save follow-up
        if st.button("💾 Save as Note"):
            add_note(selected_id, style.capitalize(), ai_response)
            st.success("AI message saved.")

