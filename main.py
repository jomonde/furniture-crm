import streamlit as st
from db import init_db, add_client, get_all_clients, delete_client, update_client, add_room_sketch, get_room_sketches_by_client, get_all_clients_with_ids

st.set_page_config(page_title="Furniture CRM", page_icon="🛋️")
init_db()

st.title("🛋️ Furniture Sales CRM")

# SESSION TRACKER FOR EDITING
if "editing" not in st.session_state:
    st.session_state.editing = None

# FORM: Add New Client
with st.form("add_form", clear_on_submit=True):
    st.subheader("➕ Add New Client")
    name = st.text_input("Full Name")
    contact = st.text_input("Phone / Email")
    room_focus = st.multiselect("Room(s) of Interest", ["Living Room", "Bedroom", "Dining", "Office", "Outdoor"])
    style_pref = st.text_input("Style Preference")
    budget = st.text_input("Estimated Budget")

    submitted = st.form_submit_button("Add Client")
    if submitted:
        add_client(name, contact, ", ".join(room_focus), style_pref, budget)
        st.success(f"{name} added successfully.")

# FORM: Sketch Helper
st.markdown("---")
st.subheader("📝 Room Sketch Helper")

# Get clients with IDs
clients_with_ids = get_all_clients_with_ids()
client_options = {f"{name} ({contact})": cid for cid, name, contact, *_ in clients_with_ids}
client_display = st.selectbox("Select Client", ["-- Select a Client --"] + list(client_options.keys()))

if client_display != "-- Select a Client --":
    selected_client_id = client_options[client_display]

    # Form for room sketch entry goes here (make it conditional)
    with st.form("sketch_form"):
        room_type = st.selectbox("Room Type", ["Living Room", "Bedroom", "Dining Room", "Office", "Outdoor", "Other"])
        dimensions = st.text_input("Room Dimensions (e.g., 12x15 ft)")
        layout_notes = st.text_area("Describe layout: windows, doors, walkways, etc.")
        current_furniture = st.text_area("Current Furniture in Room")
        desired_furniture = st.text_area("Desired Pieces (type, style, finish)")
        special_considerations = st.text_area("Anything special? (pets, kids, storage, lighting, etc.)")

        sketch_submitted = st.form_submit_button("Save Room Sketch")
        if sketch_submitted:
            add_room_sketch(selected_client_id, room_type, dimensions, layout_notes, current_furniture, desired_furniture, special_considerations)
            st.success("Room sketch saved!")

    # Display saved sketches
    sketches = get_room_sketches_by_client(selected_client_id)
    if sketches:
        st.subheader("📐 Sketches for This Client")
        for i, sketch in enumerate(sketches, 1):
            st.markdown(f"**Sketch #{i}**")
            st.markdown(f"""
            - **Room:** {sketch[0]}
            - **Dimensions:** {sketch[1]}
            - **Layout Notes:** {sketch[2]}
            - **Current Furniture:** {sketch[3]}
            - **Desired Furniture:** {sketch[4]}
            - **Special Considerations:** {sketch[5]}
            """)
else:
    st.warning("Please select a client to proceed with room sketch entry.")

# GET ALL CLIENTS
clients = get_all_clients()

# LIST & ACTIONS
if clients:
    st.subheader("📋 Current Clients")
    for idx, (name, contact, rooms, style, budget) in enumerate(clients):
        with st.expander(f"{name} — {contact}"):
            st.markdown(f"**Rooms:** {rooms}  \n**Style:** {style}  \n**Budget:** {budget}")

            col1, col2 = st.columns(2)
            if col1.button("✏️ Edit", key=f"edit_{idx}"):
                st.session_state.editing = {"original_name": name, "original_contact": contact,
                                            "name": name, "contact": contact,
                                            "rooms": rooms, "style": style, "budget": budget}
            if col2.button("🗑️ Delete", key=f"delete_{idx}"):
                delete_client(name, contact)
                st.rerun()

# IF EDITING
if st.session_state.editing:
    st.subheader("✏️ Edit Client")
    with st.form("edit_form"):
        editing = st.session_state.editing
        new_name = st.text_input("Full Name", editing["name"])
        new_contact = st.text_input("Phone / Email", editing["contact"])
        room_focus = st.text_input("Room(s)", editing["rooms"])
        style_pref = st.text_input("Style Preference", editing["style"])
        budget = st.text_input("Estimated Budget", editing["budget"])

        update = st.form_submit_button("Update Client")
        cancel = st.form_submit_button("Cancel")

        if update:
            update_client(
                editing["original_name"],
                editing["original_contact"],
                new_name, new_contact,
                room_focus, style_pref, budget
            )
            st.success("Client updated!")
            st.session_state.editing = None
            st.rerun()

        elif cancel:
            st.session_state.editing = None
