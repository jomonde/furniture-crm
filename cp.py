import streamlit as st
from db import (
    get_all_clients_with_ids,
    get_room_sketches_by_client,
    add_room_sketch,
    get_notes_by_client,
    add_note, add_client,
    update_note,
    delete_note,
    update_sale,
    void_sale,
    get_total_sales_volume_by_client, get_average_sale_by_client, get_first_sale_date_by_client, get_average_days_between_sales, get_sales_by_client
)
from ai_helper import generate_layout_and_followup

st.set_page_config(page_title="Clients", page_icon="📇")
st.title("📇 Client Profile")

if st.checkbox ("➕ Add a New Client"):
    with st.form("add_client_form"):
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        address = st.text_input("Home Address")
        rooms = st.text_input("Room(s) of Interest (e.g. Living, Bedroom)")
        style = st.text_input("Style Preference")
        budget = st.text_input("Estimated Budget")
        add_another = st.checkbox("Add another client after this?")

        submitted = st.form_submit_button("Save Client")

        if submitted:
            if not name.strip():
                st.warning("Name is required.")
            elif not (phone.strip() or email.strip() or address.strip()):
                st.warning("At least one contact method (phone, email, or address) is required.")
            else:
                add_client(name, phone, email, address, rooms, style, budget)
                st.success("Client added successfully!")

                # Reset form fields if checkbox is unchecked (simulate clear)
                if not add_another:
                    st.experimental_rerun()

# Fetch all clients
clients = get_all_clients_with_ids()
client_options = {f"{c.get('name')} ({c.get('phone') or c.get('email') or c.get('address')})": c.get("id") for c in clients}

client_display = st.selectbox("Select a client", ["-- Select Client --"] + list(client_options.keys()))

if client_display != "-- Select Client --":
    selected_id = client_options[client_display]
    client_data = next((c for c in clients if c.get("id") == selected_id), None)

    if client_data:
        st.markdown(f"### 👤 {client_data['name']}")
        st.markdown(f"""
        **Phone:** {client_data.get('phone', '')}  
        **Email:** {client_data.get('email', '')}  
        **Address:** {client_data.get('address', '')}  
        **Room Focus:** {client_data.get('rooms', '')}  
        **Style Preference:** {client_data.get('style', '')}  
        **Budget:** {client_data.get('budget', '')}
        """)

        # -------------------------------
        # ROOM SKETCHES
        # -------------------------------
        st.subheader("📐 Add a Room Sketch")

        with st.form("add_sketch_form"):
            room_type = st.selectbox("Room Type", ["Living Room", "Bedroom", "Dining Room", "Office", "Outdoor", "Other"])
            dimensions = st.text_input("Room Dimensions (e.g., 12x15 ft)")
            layout_notes = st.text_area("Layout Notes (windows, walkways, etc.)")
            current_furniture = st.text_area("Current Furniture")
            desired_furniture = st.text_area("Desired Pieces")
            special_considerations = st.text_area("Special Considerations (pets, kids, lighting, etc.)")
            sketch_submit = st.form_submit_button("Save Sketch")

            if sketch_submit:
                add_room_sketch(selected_id, room_type, dimensions, layout_notes, current_furniture, desired_furniture, special_considerations)
                st.success("Sketch saved!")
                st.experimental_rerun()

        sketches = get_room_sketches_by_client(selected_id)
        if sketches:
            st.subheader("📋 Saved Sketches")
            for i, sketch in enumerate(sketches, 1):
                with st.expander(f"Sketch #{i}: {sketch['room_type']}"):
                    st.markdown(f"""
                    **Dimensions:** {sketch['dimensions']}  
                    **Layout Notes:** {sketch['layout_notes']}  
                    **Current Furniture:** {sketch['current_furniture']}  
                    **Desired Furniture:** {sketch['desired_furniture']}  
                    **Special Considerations:** {sketch['special_considerations']}
                    """)

        # -------------------------------
        # AI LAYOUT & FOLLOW-UP
        # -------------------------------
        if sketches:
            st.subheader("🤖 AI Layout & Follow-Up Generator")

            # Use latest sketch by default
            latest_sketch = sketches[-1]

            with st.form("ai_form"):
                st.markdown("Generate layout tips and a personalized follow-up message based on the latest sketch.")
                style = client_data.get("style", "")
                budget = client_data.get("budget", "")
                generate = st.form_submit_button("Generate AI Note")

                if generate:
                    sketch_data = {
                        "room_type": latest_sketch["room_type"],
                        "dimensions": latest_sketch["dimensions"],
                        "layout_notes": latest_sketch["layout_notes"],
                        "current_furniture": latest_sketch["current_furniture"],
                        "desired_furniture": latest_sketch["desired_furniture"],
                        "special_considerations": latest_sketch["special_considerations"],
                        "style": style,
                        "budget": budget
                    }
                    result = generate_layout_and_followup(sketch_data)
                    add_note(selected_id, "AI", result)
                    st.success("AI note added to client profile.")
                    st.markdown(result)
                    st.experimental_rerun()

        # -------------------------------
        # NOTES SECTION
        # -------------------------------
        # -------------------------------
        # ADD A MANUAL NOTE
        # -------------------------------
        st.subheader("➕ Add Manual Note")

        with st.form("manual_note_form"):
            note_type = st.selectbox("Note Type", ["Manual", "Follow-Up", "Consultation", "Other"])
            content = st.text_area("Note Content", height=150)
            note_submit = st.form_submit_button("Add Note")

            if note_submit:
                if not content.strip():
                    st.warning("Note content cannot be empty.")
                else:
                    add_note(selected_id, note_type, content)
                    st.success("Note added.")
                    st.experimental_rerun()

        st.subheader("🗒️ Notes")
        notes = get_notes_by_client(selected_id)

        if notes:
            for note in notes:
                with st.expander(f"🕒 {note['timestamp']} | 🏷️ {note['type']}"):
                    edited = st.text_area("Edit Note", note["content"], key=f"edit_{note['id']}")
                    col1, col2 = st.columns(2)
                    if col1.button("💾 Save", key=f"save_{note['id']}"):
                        update_note(note["id"], edited)
                        st.success("Note updated!")
                        st.experimental_rerun()
                    if col2.button("🗑️ Delete", key=f"delete_{note['id']}"):
                        delete_note(note["id"])
                        st.warning("Note deleted.")
                        st.experimental_rerun()
        else:
            st.info("No notes found for this client.")

        # -------------------------------
        # SALES HISTORY WITH FILTERS
        # -------------------------------
        st.subheader("💵 Sales History")

        # Lifetime Stats
        total_volume = get_total_sales_volume_by_client(selected_id)
        average_sale = get_average_sale_by_client(selected_id)

        st.markdown(f"**Total Sales Volume:** ${total_volume:,.2f}")
        st.markdown(f"**Average Sale:** ${average_sale:,.2f}")

        first_date = get_first_sale_date_by_client(selected_id)
        avg_days = get_average_days_between_sales(selected_id)

        if first_date:
            st.markdown(f"**First Purchase Date:** {first_date}")
        else:
            st.markdown("**First Purchase Date:** —")

        if avg_days:
            st.markdown(f"**Avg Time Between Sales:** {avg_days} days")
        else:
            st.markdown("**Avg Time Between Sales:** —")

        # Filter + Sort Controls
        col1, col2 = st.columns(2)
        selected_status = col1.selectbox("Filter by Status", ["All","Unsold", "Open", "Closed", "Void"])
        sort_order = col2.radio("Sort by Date", ["Newest First", "Oldest First"])

        sales = get_sales_by_client(selected_id)

        # Apply filters
        if selected_status != "All":
            sales = [s for s in sales if s["status"] == selected_status]

        # Sort sales
        sales = sorted(sales, key=lambda x: x["date"], reverse=(sort_order == "Newest First"))

        if sales:
            for sale in sales:
                with st.expander(f"🧾 {sale['date']} – ${sale['amount']:,.2f} – {sale['status']}"):
                    new_amount = st.number_input("Amount", value=sale["amount"], key=f"amt_{sale['id']}")
                    new_status = st.selectbox("Status", ["Unsold", "Open", "Closed", "Void"], index=["Unsold", "Open", "Closed", "Void"].index(sale["status"]), key=f"status_{sale['id']}")
                    new_notes = st.text_area("Notes", value=sale.get("notes", ""), key=f"note_{sale['id']}")

                    col1, col2 = st.columns(2)
                    if col1.button("💾 Save Changes", key=f"save_{sale['id']}"):
                        update_sale(sale["id"], new_amount, new_status, new_notes)
                        st.success("Sale updated!")
                        st.experimental_rerun()

                    if col2.button("🗑️ Void Sale", key=f"void_{sale['id']}"):
                        void_sale(sale["id"])
                        st.warning("Sale voided.")
                        st.experimental_rerun()
        else:
            st.info("No sales to display for the selected filters.")


