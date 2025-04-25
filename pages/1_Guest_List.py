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
    add_client
)
from engines.sketch_engine import generate_sketch_summary
from engines.message_engine import generate_followup_message
from engines.client_engine import gather_client_history, generate_client_summary

st.set_page_config(page_title="Clients", page_icon="👥")
st.title("👥 Clients")

# -------------------------------
# CLIENT SELECTION
# -------------------------------
clients = get_all_clients_with_ids()
client_options = {f"{c['name']} ({c['phone']})": c["id"] for c in clients}
st.markdown("### ➕ Add New Client")
with st.expander("New Client Form", expanded=False):
    with st.form("add_new_client"):
        new_name = st.text_input("Name")
        new_phone = st.text_input("Phone")
        new_email = st.text_input("Email")
        new_address = st.text_input("Address")
        new_rooms = st.text_input("Rooms of Interest")
        new_style = st.text_input("Style Preference")
        new_budget = st.text_input("Budget")
        new_status = st.selectbox("Status", ["active", "inactive"])
        submit_new = st.form_submit_button("Add Client")

        if submit_new and new_name and new_phone:
            add_client(new_name, new_phone, new_email, new_address, new_rooms, new_style, new_budget, new_status)
            st.success(f"Client '{new_name}' added successfully.")
            st.rerun()

# 🔍 Searchable client dropdown
st.markdown("### 🔎 Select a Client to View Details")
search_term = st.text_input("Search Client by Name or Phone")
filtered_clients = {
    label: cid for label, cid in client_options.items()
    if search_term.lower() in label.lower()
}

client_display = st.selectbox("Client List", ["-- Select --"] + list(filtered_clients.keys()))

if client_display != "-- Select --":
    selected_id = client_options[client_display]
    client_data = get_client_by_id(selected_id)
    sketches = get_room_sketches_by_client(selected_id)
    notes = get_notes_by_client(selected_id)

    # -------------------------------
    # CLIENT INFO + EDIT FORM
    # -------------------------------
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

    # -------------------------------
    # CLIENT SUMMARY
    # -------------------------------
    client_data = gather_client_history(selected_id)
    summary = generate_client_summary(client_data)

    st.markdown("### 🧠 Client Summary")
    st.markdown(summary)

    # -------------------------------
    # ADD ROOM SKETCH
    # -------------------------------
    with st.expander("📐 Add Room Sketch"):
        with st.form("add_sketch_form", clear_on_submit=True):
            room_type = st.selectbox("Room Type", ["Living Room", "Bedroom", "Dining", "Office", "Outdoor", "Other"])
            dimensions = st.text_input("Dimensions")
            layout_notes = st.text_area("Layout Notes")
            current_furniture = st.text_area("Current Furniture")
            desired_furniture = st.text_area("Desired Furniture")
            special_considerations = st.text_area("Special Considerations")

            if st.form_submit_button("Save Sketch"):
                add_room_sketch(selected_id, room_type, dimensions, layout_notes, current_furniture, desired_furniture, special_considerations)
                st.success("Sketch saved.")
                st.rerun()

    # -------------------------------
    # DISPLAY SKETCHES + AI SUMMARIES
    # -------------------------------
    if sketches:
        st.subheader("📐 Saved Sketches")
        for sketch in sketches[::-1]:
            created_at = sketch.get("created_at", "Unknown Date")
            title = f"{sketch['room_type']} — {created_at[:10]}"
            with st.expander(title):
                st.markdown(f"**Dimensions:** {sketch['dimensions']}")
                st.markdown(f"**Current Furniture:** {sketch['current_furniture']}")
                st.markdown(f"**Desired Furniture:** {sketch['desired_furniture']}")
                st.markdown(f"**Special Considerations:** {sketch['special_considerations']}")
                if st.button(f"🧠 Summarize Layout ({title})", key=f"sketch_summary_{sketch['id']}"):
                    summary = generate_sketch_summary(sketch, client_data)
                    st.markdown("**🪄 AI Summary:**")
                    st.markdown(summary)

    # -------------------------------
    # NOTES + AI GENERATION
    # -------------------------------
    st.subheader("🗒️ Notes")

    for note in notes[::-1]:
        with st.expander(f"{note['timestamp'][:10]} — {note['type']}"):
            st.markdown(note["content"])

    st.markdown("### ✍️ Add Manual Note")
    with st.form("manual_note_form", clear_on_submit=True):
        manual_note = st.text_area("Write your note")
        save_note = st.form_submit_button("Save Note")
        if save_note and manual_note.strip():
            add_note(selected_id, "Manual", manual_note)
            st.success("Note saved.")
            st.rerun()

    st.markdown("### 🤖 Generate Note with AI")
    with st.form("ai_note_form"):
        client_type = st.selectbox("Guest Type", ["bought", "browsed"])
        message_style = st.selectbox("Message Style", ["text", "phone", "email", "handwritten"])
        prompt = st.text_input("Prompt (e.g. follow-up idea, call script, layout message)")
        submit_ai = st.form_submit_button("Generate")

        if submit_ai:
            msg = generate_followup_message(client_type, message_style, client_data, sketches[-1] if sketches else {})
            st.markdown("**🧠 AI Note Suggestion:**")
            st.markdown(msg)
            if st.button("💾 Save This Note"):
                add_note(selected_id, message_style.capitalize(), msg)
                st.success("AI note saved.")
                st.rerun()

    # -------------------------------
    # 📦 SALES HISTORY
    # -------------------------------
    st.subheader("📦 Sales History")

    sales = get_sales_by_client(selected_id)

    if sales:
        for sale in sales:
            with st.expander(f"${sale['amount']} — {sale['status']} ({sale['date'][:10]})", expanded=False):
                st.markdown(f"**Amount:** ${sale['amount']}")
                st.markdown(f"**Status:** {sale['status']}")
                st.markdown(f"**Notes:** {sale.get('notes', '') or '—'}")

                with st.form(f"update_sale_{sale['id']}", clear_on_submit=False):
                    new_amount = st.number_input("Amount", value=float(sale["amount"]), step=10.0)
                    new_status = st.selectbox("Status", ["Open", "Closed", "Void", "Unsold"], index=["Open", "Closed", "Void", "Unsold"].index(sale["status"]))
                    new_notes = st.text_area("Notes", value=sale.get("notes", ""))
                    update = st.form_submit_button("Update Sale")

                    if update:
                        update_sale(sale["id"], new_amount, new_status, new_notes)
                        st.success("Sale updated!")
                        st.rerun()
    else:
        st.info("No sales recorded for this client.")

    # -------------------------------
    # 📋 TASKS FOR THIS CLIENT
    # -------------------------------
    st.subheader("📋 Client Tasks")

    tasks = get_tasks_by_client(selected_id)
    open_tasks = [t for t in tasks if not t["completed"]]
    completed_tasks = [t for t in tasks if t["completed"]]

    if open_tasks:
        st.markdown("### 🟡 Open Tasks")
        for task in open_tasks:
            label = f"{task['description']} — due {task['due_date']}"
            if task.get("message"):
                st.markdown(f"💬 *Suggested Message:* {task['message']}")
            if st.checkbox(label, key=f"task_{task['id']}"):
                complete_task(task["id"])
                st.success("Task marked complete.")
                st.rerun()
    else:
        st.info("No open tasks.")

    if completed_tasks:
        with st.expander("✅ Completed Tasks"):
            for task in completed_tasks:
                st.markdown(f"- {task['description']} — done on {task['due_date']}")
    else:
        st.info("No completed tasks yet.")
