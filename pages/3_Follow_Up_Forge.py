import streamlit as st
from datetime import date
from db import get_all_clients_with_ids, add_note, add_task, get_tasks_by_date, complete_task
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

    # Select follow-up type
    guest_type = st.selectbox("Guest Type", ["bought", "browsed"])
    style = st.selectbox("Message Style", ["text", "phone", "email", "handwritten"])

    if st.button("📋 Generate Follow-Up"):
        template = followup_templates.get(guest_type, {}).get(style)

        if isinstance(template, dict):
            st.markdown(f"**Subject:** {template['subject']}")
            st.markdown(template["body"])
            message = f"Subject: {template['subject']}\n\n{template['body']}"
        else:
            st.markdown(template)
            message = template

        if st.button("💾 Save and Create Task"):
            add_note(selected_id, style.capitalize(), message)
            add_task(selected_id, f"{style.capitalize()} follow-up", date.today().isoformat())
            st.success("Note saved and task created.")

# Task list
st.markdown("---")
st.subheader("📅 Today's Follow-Up Tasks")

tasks = get_tasks_by_date(date.today().isoformat())

if not tasks:
    st.info("No tasks scheduled for today.")
else:
    for task in tasks:
        label = f"{task['description']} for client ID {task['client_id']}"
        checked = st.checkbox(label, value=task["completed"], key=task["id"])
        if checked and not task["completed"]:
            complete_task(task["id"])
            st.success("Task marked as complete.")
            st.rerun()
