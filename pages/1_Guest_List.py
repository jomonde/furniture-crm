import streamlit as st
from db import (
    get_all_clients_with_ids,
    get_client_by_id,
    update_client,
    get_room_sketches_by_client,
    add_room_sketch,
    get_notes_by_client,
    add_note,
    get_sales_by_client,
    update_sale,
    get_tasks_by_client,
    complete_task,
    update_client_summary,
    compute_client_last_modified
)
from engines.sketch_engine import generate_sketch_summary
from engines.message_engine import generate_followup_message
from engines.client_engine import gather_client_history, generate_client_summary
from datetime import datetime

# --- Page Setup ---
st.set_page_config(page_title="Guest List", page_icon="👥", layout="wide")
st.title("👥 The Guest List")

# --- Client Selection ---
clients = get_all_clients_with_ids()
client_options = {f"{c['name']} ({c['phone']})": c["id"] for c in clients}

search_term = st.text_input("🔍 Search for Client (name or phone)")
filtered_clients = [label for label in client_options if search_term.lower() in label.lower()]
selected_client = st.selectbox("Select Client", filtered_clients if filtered_clients else ["No matches found"])

if selected_client != "No matches found":
    selected_id = client_options[selected_client]
    client_data = get_client_by_id(selected_id)

    # --- Client Info Section ---
    with st.expander("📝 Client Info", expanded=True):
        with st.form("edit_client_info"):
            name = st.text_input("Name", client_data["name"])
            phone = st.text_input("Phone", client_data["phone"])
            email = st.text_input("Email", client_data["email"])
            address = st.text_input("Address", client_data["address"])
            rooms = st.text_input("Rooms of Interest", client_data["rooms"])
            style = st.text_input("Style Preference", client_data["style"])
            budget = st.text_input("Budget", client_data["budget"])
            status = st.selectbox("Status", ["active", "inactive"], index=0 if client_data["status"] == "active" else 1)

            save_info = st.form_submit_button("💾 Save Changes")

            if save_info:
                update_client(selected_id, name, phone, email, address, rooms, style, budget, status)
                st.success("Client updated.")
                st.rerun()

        # Display last contact info
        last_contact = client_data.get("last_contact")
        if last_contact:
            days_since = (datetime.utcnow() - datetime.fromisoformat(last_contact)).days
            st.caption(f"🕰️ Last Contact: {days_since} days ago ({last_contact[:10]})")
        else:
            st.caption("🕰️ Last Contact: Never")

    # --- Smart Client Summary (with caching) ---
    st.markdown("### 🧠 Client Summary")

    # Gather full client history
    full_history = gather_client_history(selected_id)

    # Check if summary is fresh
    existing_summary = client_data.get("client_summary")
    summary_last_updated = client_data.get("summary_last_updated")
    client_last_modified = compute_client_last_modified(selected_id)

    needs_regeneration = (
        not existing_summary or
        not summary_last_updated or
        summary_last_updated < client_last_modified
    )

    if needs_regeneration:
        summary_text = generate_client_summary(full_history)
        update_client_summary(selected_id, summary_text)
    else:
        summary_text = existing_summary

    # Collapsible AI Summary
    with st.expander("🧠 View Client Summary", expanded=False):
        st.markdown(summary_text)

    # --- Room Sketches ---
    sketches = get_room_sketches_by_client(selected_id)
    st.markdown("### 📐 Room Sketches")

    with st.expander("➕ Add New Sketch"):
        with st.form("add_sketch_form", clear_on_submit=True):
            room_type = st.selectbox("Room Type", ["Living Room", "Bedroom", "Dining", "Office", "Outdoor", "Other"])
            dimensions = st.text_input("Dimensions")
            layout_notes = st.text_area("Layout Notes")
            current_furniture = st.text_area("Current Furniture")
            desired_furniture = st.text_area("Desired Furniture")
            special_considerations = st.text_area("Special Considerations")

            save_sketch = st.form_submit_button("Save Sketch")
            if save_sketch:
                add_room_sketch(selected_id, room_type, dimensions, layout_notes, current_furniture, desired_furniture, special_considerations)
                st.success("Sketch saved.")
                st.rerun()

    if sketches:
        for sketch in sketches[::-1]:
            created_at = sketch.get('created_at', 'Unknown Date')
            title = f"{sketch['room_type']} — {created_at[:10] if created_at != 'Unknown Date' else 'No Date'}"

            with st.expander(title):
                st.markdown(f"**Dimensions:** {sketch['dimensions']}")
                st.markdown(f"**Current Furniture:** {sketch['current_furniture']}")
                st.markdown(f"**Desired Furniture:** {sketch['desired_furniture']}")
                st.markdown(f"**Special Considerations:** {sketch['special_considerations']}")
                if st.button(f"🧠 Summarize Layout", key=f"sketch_summary_{sketch['id']}"):
                    sketch_summary = generate_sketch_summary(sketch, client_data)
                    st.markdown("**🪄 AI Layout Summary:**")
                    st.markdown(sketch_summary)

    # --- Notes and AI Follow-Up Generator ---
    st.markdown("### 🗒️ Notes & Messages")

    notes = get_notes_by_client(selected_id)
    for note in notes[::-1]:
        with st.expander(f"{note['timestamp'][:10]} — {note['type']}"):
            st.markdown(note["content"])

    with st.expander("➕ Add Note or Follow-Up"):
        with st.form("add_note_form", clear_on_submit=True):
            manual_note = st.text_area("Write a Manual Note or Message")
            client_type = st.selectbox("Client Type", ["bought", "browsed"])
            message_style = st.selectbox("Message Style", ["text", "phone", "email", "handwritten"])
            generate = st.form_submit_button("Generate AI Message")
            save_manual = st.form_submit_button("Save Manual Note")

            if save_manual and manual_note.strip():
                add_note(selected_id, "Manual", manual_note)
                from db import update_last_contact
                update_last_contact(selected_id)
                st.success("Manual note saved.")
                st.rerun()

            if generate:
                ai_message = generate_followup_message(client_type, message_style, client_data, sketches[-1] if sketches else {})
                add_note(selected_id, message_style.capitalize(), ai_message)
                from db import update_last_contact
                update_last_contact(selected_id)
                st.success("AI message saved.")
                st.rerun()

    # --- Sales History ---
    st.markdown("### 📦 Sales History")

    sales = get_sales_by_client(selected_id)
    if sales:
        for sale in sales:
            with st.expander(f"${sale['amount']} — {sale['status']} ({sale['date'][:10]})"):
                st.markdown(f"**Amount:** ${sale['amount']}")
                st.markdown(f"**Status:** {sale['status']}")
                st.markdown(f"**Notes:** {sale.get('notes', '-')}")
    else:
        st.info("No sales recorded yet.")

    # --- Add a Sale ---
    with st.expander("➕ Add Sale for This Client"):
        from components.sale_form import sale_entry_form  # Adjust path if needed
        sale_entry_form(selected_client_id=selected_id)

    # --- Related Tasks ---
    st.markdown("### 📋 Related Tasks")

    tasks = get_tasks_by_client(selected_id)
    open_tasks = [t for t in tasks if not t["completed"]]
    completed_tasks = [t for t in tasks if t["completed"]]

    if open_tasks:
        st.markdown("#### 🟡 Open Tasks")
        for task in open_tasks:
            if st.checkbox(f"{task['description']} — Due {task['due_date']}", key=f"task_complete_{task['id']}"):
                complete_task(task["id"])
                st.success("Task marked complete.")
                st.rerun()
    else:
        st.info("No open tasks.")

    if completed_tasks:
        with st.expander("✅ Completed Tasks"):
            for task in completed_tasks:
                st.markdown(f"- {task['description']} — Done {task['due_date']}")

