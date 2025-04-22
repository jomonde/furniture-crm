import streamlit as st
from db import (
    get_all_clients_with_ids,
    get_client_by_id,
    update_client,
    get_room_sketches_by_client,
    add_room_sketch,
    get_notes_by_client,
    add_note,
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
st.subheader("🗒️ Notes")

notes = get_notes_by_client(selected_id)
for note in notes:
    st.markdown(f"- *{note['timestamp'][:10]}*: {note['content']}")

st.markdown("---")

st.markdown("**Generate New Note with AI**")

if "ai_result" not in st.session_state:
    st.session_state.ai_result = ""

with st.form("ai_note_form"):
    prompt = st.text_input("Prompt (e.g., follow-up text, room suggestion)")
    generate = st.form_submit_button("Generate Note")

if generate and prompt.strip():
    with st.spinner("Thinking..."):
        sketch_context = sketches[-1] if sketches else {}
        result = generate_note_from_prompt(prompt, client_data, sketch_context)
    st.session_state.ai_result = result
    st.success("Note generated!")
    st.markdown(result)

if st.session_state.ai_result:
    st.markdown(st.session_state.ai_result)
    if st.button("💾 Save This Note"):
        add_note(selected_id, "AI Helped", st.session_state.ai_result)
        st.success("Note saved.")
        st.session_state.ai_result = ""  # Clear after saving
        st.rerun()

st.markdown("### ✍️ Add Manual Note")

with st.form("manual_note_form", clear_on_submit=True):
    manual_note = st.text_area("Write your note")
    save_note = st.form_submit_button("💾 Save This Note")

    if save_note and manual_note.strip():
        add_note(selected_id, "Manual", manual_note)
        st.success("Note saved.")
        st.rerun()

