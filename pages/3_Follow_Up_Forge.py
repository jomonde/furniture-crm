import streamlit as st
from datetime import date
from db import (
    get_all_clients_with_ids,
    get_client_by_id,
    get_room_sketches_by_client,
    add_note,
)
from ai_helper import generate_followup_from_template

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

    # Select follow-up type and style
    guest_type = st.selectbox("Guest Type", ["bought", "browsed"])
    style = st.selectbox("Message Style", ["text", "phone", "email", "handwritten"])

    if st.button("📋 Generate AI Follow-Up"):
        with st.spinner("Talking to the AI..."):
            ai_response = generate_followup_from_template(
                client_type=guest_type,
                message_style=style,
                client_data=client_data,
                sketch_data=latest_sketch
            )

        st.markdown("### 🧠 AI-Generated Message")
        st.markdown(ai_response)

        if st.button("💾 Save as Note"):
            add_note(selected_id, style.capitalize(), ai_response)
            st.success("AI message saved.")
