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
)
from ai_helper import generate_note_from_prompt
from datetime import datetime

st.set_page_config(page_title="Clients", page_icon="📇")
st.title("📇 Client Profile")

# -------------------------------
# SELECT CLIENT
# -------------------------------
clients = get_all_clients_with_ids()
client_options = {f"{c['name']} ({c['phone']})": c['id'] for c in clients}
selected_name = st.selectbox("Select Client", ["-- Select Client --"] + list(client_options.keys()))

if selected_name == "-- Select Client --":
    st.stop()

selected_id = client_options[selected_name]
client_data = get_client_by_id(selected_id)

if not client_data:
    st.error("Client not found.")
    st.stop()

# -------------------------------
# CLIENT INFO (Editable)
# -------------------------------
st.subheader("🧾 Client Info")

edit_mode = st.checkbox("✏️ Edit Client Info")
if edit_mode:
    with st.form("edit_client"):
        name = st.text_input("Full Name", value=client_data["name"])
        phone = st.text_input("Phone", value=client_data["phone"])
        email = st.text_input("Email", value=client_data["email"])
        address = st.text_input("Address", value=client_data["address"])
        rooms = st.text_input("Room(s) of Interest", value=client_data["rooms"])
        style = st.text_input("Style Preference", value=client_data["style"])
        budget = st.text_input("Estimated Budget", value=client_data["budget"])

        if st.form_submit_button("Save Changes"):
            update_client(selected_id, name, phone, email, address, rooms, style, budget)
            st.success("Client info updated!")
            st.rerun()
else:
    st.markdown(f"""
    **Name:** {client_data['name']}  
    **Phone:** {client_data['phone']}  
    **Email:** {client_data['email']}  
    **Address:** {client_data['address']}  
    **Rooms:** {client_data['rooms']}  
    **Style:** {client_data['style']}  
    **Budget:** {client_data['budget']}  
    """)

# -------------------------------
# SALES HISTORY
# -------------------------------
st.subheader("💰 Sales History")

sales = get_sales_by_client(selected_id)

if not sales:
    st.info("No sales recorded yet for this client.")
else:
    sales = sorted(sales, key=lambda s: s["date"], reverse=True)

    for sale in sales:
        sale_id = sale["id"]
        date_str = datetime.fromisoformat(sale["date"]).strftime('%b %d, %Y')
        header = f"Sale on {date_str} – ${sale['amount']} ({sale['status']})"
        
        with st.expander(header):
            new_amount = st.number_input(
                "💵 Sale Amount",
                value=float(sale["amount"]),
                key=f"amount_{sale_id}"
            )

            new_status = st.selectbox(
                "🔄 Status",
                options=["Open", "Closed", "Unsold", "Void"],
                index=["Open", "Closed", "Unsold", "Void"].index(sale["status"]),
                key=f"status_{sale_id}"
            )

            new_notes = st.text_area(
                "📝 Notes",
                value=sale.get("notes", ""),
                key=f"notes_{sale_id}"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Sale Updates", key=f"save_{sale_id}"):
                    update_sale(sale_id, new_amount, new_status, new_notes)
                    st.success("Sale updated successfully.")
                    st.rerun()
            with col2:
                if st.button("🗑️ Mark as Void", key=f"void_{sale_id}") and sale["status"] != "Void":
                    update_sale(sale_id, new_amount, "Void", new_notes)
                    st.success("Sale marked as Void.")
                    st.rerun()

# -------------------------------
# SKETCH ENTRY (Toggle + List)
# -------------------------------
st.subheader("📐 Room Sketches")
if st.checkbox("➕ Add a New Sketch"):
    with st.form("sketch_form"):
        room_type = st.text_input("Room Type")
        dimensions = st.text_input("Room Dimensions")
        layout_notes = st.text_area("Layout Notes")
        current_furniture = st.text_area("Current Furniture")
        desired_furniture = st.text_area("Desired Furniture")
        special_considerations = st.text_area("Special Considerations")
        submit = st.form_submit_button("Save Sketch")
        if submit:
            add_room_sketch(selected_id, room_type, dimensions, layout_notes, current_furniture, desired_furniture, special_considerations)
            st.success("Sketch saved!")
            st.rerun()

# Show saved sketches
sketches = get_room_sketches_by_client(selected_id)
if sketches:
    for sketch in sketches:
        created_at = sketch.get("created_at", datetime.now().isoformat())
        try:
            display_date = datetime.fromisoformat(created_at).strftime('%b %d, %Y')
        except:
            display_date = created_at.split("T")[0]

        title = f"{sketch['room_type']} – {display_date}"
        with st.expander(title):
            st.markdown(f"""
            **Dimensions:** {sketch['dimensions']}  
            **Layout Notes:** {sketch['layout_notes']}  
            **Current Furniture:** {sketch['current_furniture']}  
            **Desired Furniture:** {sketch['desired_furniture']}  
            **Special Considerations:** {sketch['special_considerations']}
            """)

# -------------------------------
# NOTES + AI GENERATION
# -------------------------------
st.subheader("🗒️ Client Notes")

notes = get_notes_by_client(selected_id)

if not notes:
    st.info("No notes yet for this client.")
else:
    for i, note in enumerate(notes):
        # Create a preview: first line, max 100 characters
        preview = note["content"].strip().split("\n")[0][:100]
        label = f"{note['timestamp'][:10]} – {preview}{'...' if len(preview) == 100 else ''}"

        with st.expander(label):
            st.markdown(note["content"])

st.markdown("---")

st.markdown("### ✍️ Add Note")

with st.form("manual_note_form", clear_on_submit=True):
    manual_note = st.text_area("Write your note")
    save_note = st.form_submit_button("💾 Save This Note")

    if save_note and manual_note.strip():
        add_note(selected_id, "Manual", manual_note)
        st.success("Note saved.")
        st.rerun()

st.subheader("✅ Task History")

tasks = get_tasks_by_client(selected_id)

if not tasks:
    st.info("No tasks yet for this client.")
else:
    for task in tasks:
        label = f"{task['description']} — due {task['due_date']}"
        if not task["completed"]:
            checked = st.checkbox(label, key=f"task_{task['id']}")
            if checked:
                complete_task(task["id"])
                st.success("Task marked complete.")
                st.rerun()
        else:
            st.markdown(f"🗂️ **Completed:** {label} (on {task['due_date']})")