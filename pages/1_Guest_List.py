import streamlit as st
from db import (
    get_all_clients_with_ids,
    update_client,
    add_client,
    safe_fetch_client_data,
    update_client_summary
)
from engines.sketch_engine import generate_sketch_summary
from engines.message_engine import generate_followup_message
from engines.client_engine import generate_client_summary

st.set_page_config(page_title="Clients", page_icon="👥", layout="wide")
st.title("👥 Guest List (Clients)")

# --- Client Selection ---
clients = get_all_clients_with_ids()
client_options = {f"{c['name']} ({c['phone']})": c["id"] for c in clients}

# Insert 'Add New Client' at the top
client_labels = ["➕ Add New Client"] + list(client_options.keys())

search_term = st.text_input("🔍 Search for Client (name or phone)")

# Apply search filter AFTER adding 'Add New Client'
if search_term:
    filtered_clients = ["➕ Add New Client"] + [label for label in client_options if search_term.lower() in label.lower()]
else:
    filtered_clients = client_labels

selected_client = st.selectbox("Select Client", filtered_clients)

# --- Initialize ---
selected_id = None
is_new_client = False

# --- Handle Client Selection ---
if selected_client == "➕ Add New Client":
    client_data = {
        "name": "",
        "phone": "",
        "email": "",
        "address": "",
        "rooms": "",
        "style": "",
        "budget": "",
        "status": "active"
    }
    sketches = []
    notes = []
    sales = []
    tasks = []
    full_history = None
    client_last_modified = None
    is_new_client = True
elif selected_client != "No matches found":
    selected_id = client_options[selected_client]
    # Use safe_fetch_client_data
    bundle = safe_fetch_client_data(selected_id)

    client_data = bundle["client_data"]
    sketches = bundle["sketches"]
    notes = bundle["notes"]
    sales = bundle["sales"]
    tasks = bundle["tasks"]
    full_history = bundle["full_history"]
    client_last_modified = bundle["client_last_modified"]
else:
    client_data = None
    sketches = []
    notes = []
    sales = []
    tasks = []
    full_history = None
    client_last_modified = None

# --- Client Info Panel ---
if client_data:
    with st.expander("📝 Client Info", expanded=True):
        with st.form("client_info_form", clear_on_submit=False):
            name = st.text_input("Name", client_data["name"])
            phone = st.text_input("Phone", client_data["phone"])
            email = st.text_input("Email", client_data["email"])
            address = st.text_input("Address", client_data["address"])
            rooms = st.text_input("Rooms of Interest", client_data["rooms"])
            style = st.text_input("Style Preference", client_data["style"])
            budget = st.text_input("Budget", client_data["budget"])
            status = st.selectbox("Status", ["active", "inactive"], index=0 if client_data.get("status", "active") == "active" else 1)
            save_info = st.form_submit_button("💾 Save Changes")

            if save_info:
                if is_new_client:
                    add_client(name, phone, email, address, rooms, style, budget)
                    st.success("✅ New client added!")
                else:
                    update_client(selected_id, name, phone, email, address, rooms, style, budget, status)
                    st.success("✅ Client updated.")

                st.rerun()

# --- Client Summary ---
if full_history:
    summary_last_updated = client_data.get("summary_last_updated")
    needs_regeneration = (
        not client_data.get("client_summary") or
        not summary_last_updated or
        (client_last_modified and summary_last_updated < client_last_modified)
    )

    if needs_regeneration:
        summary_text = generate_client_summary(full_history)
        update_client_summary(selected_id, summary_text)
    else:
        summary_text = client_data.get("client_summary", "No summary available.")
else:
    summary_text = "No client selected."

with st.expander("🧠 Client Summary", expanded=False):
    st.markdown(summary_text)

# --- Room Sketches ---
st.subheader("📐 Room Sketches")
if sketches:
    for sketch in sketches[::-1]:
        created_at = sketch.get("created_at")
        title = f"{sketch['room_type']} — {created_at[:10] if created_at else 'No Date'}"
        with st.expander(title):
            st.markdown(f"**Dimensions:** {sketch['dimensions']}")
            st.markdown(f"**Current Furniture:** {sketch['current_furniture']}")
            st.markdown(f"**Desired Furniture:** {sketch['desired_furniture']}")
            st.markdown(f"**Special Considerations:** {sketch['special_considerations']}")
            if st.button(f"🧠 Summarize Layout", key=f"sketch_summary_{sketch['id']}"):
                layout_summary = generate_sketch_summary(sketch, client_data)
                st.markdown("**🪄 Layout Summary:**")
                st.markdown(layout_summary)
else:
    st.info("No sketches available.")

# --- Notes ---
st.subheader("🗒️ Client Notes")
if notes:
    for note in notes[::-1]:
        with st.expander(f"{note['timestamp'][:10]} — {note['type']}"):
            st.markdown(note["content"])
else:
    st.info("No notes available.")

# --- Sales History ---
st.subheader("📦 Sales History")
if sales:
    for sale in sales:
        with st.expander(f"${sale['amount']} — {sale['status']} — {sale['date'][:10]}"):
            st.markdown(f"**Amount:** ${sale['amount']}")
            st.markdown(f"**Status:** {sale['status']}")
            st.markdown(f"**Notes:** {sale.get('notes', '-')}")
else:
    st.info("No sales history.")

# --- Tasks ---
st.subheader("📋 Client Tasks")
if tasks:
    open_tasks = [t for t in tasks if not t["completed"]]
    completed_tasks = [t for t in tasks if t["completed"]]

    if open_tasks:
        st.markdown("### 🟡 Open Tasks")
        for task in open_tasks:
            st.markdown(f"🔲 {task['description']} (Due {task['due_date']})")
    else:
        st.info("No open tasks.")

    if completed_tasks:
        with st.expander("✅ Completed Tasks"):
            for task in completed_tasks:
                st.markdown(f"☑️ {task['description']} (Completed {task['due_date']})")
else:
    st.info("No tasks available.")
