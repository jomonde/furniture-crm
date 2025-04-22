import streamlit as st
from ai_helper import generate_layout_and_followup
from db import get_all_clients_with_ids, get_room_sketches_by_client, update_client_notes, add_note

st.set_page_config(page_title="AI Layout & Follow-Up", page_icon="🤖")
st.title("🤖 AI Layout & Follow-Up Assistant")

st.markdown("Select a client to auto-fill their info from the CRM and Room Sketch data.")

# Load clients
clients = get_all_clients_with_ids()
client_options = {f"{name} ({contact})": cid for cid, name, contact, *_ in clients}

client_display = st.selectbox("Select Client", ["-- Select Client --"] + list(client_options.keys()))

if client_display != "-- Select Client --":
    selected_id = client_options[client_display]

    # Fetch client info
    client_data = next((c for c in clients if c[0] == selected_id), None)
    sketches = get_room_sketches_by_client(selected_id)
    sketch = sketches[-1] if sketches else None  # get latest sketch if available

    # Fallbacks for empty sketches
    sketch_data = {
        "room_type": client_data[3],  # rooms
        "dimensions": sketch[1] if sketch else "",
        "layout_notes": sketch[2] if sketch else "",
        "current_furniture": sketch[3] if sketch else "",
        "desired_furniture": sketch[4] if sketch else "",
        "special_considerations": sketch[5] if sketch else "",
        "style": client_data[4],  # style
        "budget": client_data[5]   # budget
    }

    st.markdown("### ✏️ Review or Tweak Auto-Filled Info Before Generating")

    with st.form("ai_form"):
        room_type = st.text_input("Room Type", sketch_data["room_type"])
        dimensions = st.text_input("Room Dimensions", sketch_data["dimensions"])
        layout_notes = st.text_area("Layout Notes", sketch_data["layout_notes"])
        current_furniture = st.text_area("Current Furniture", sketch_data["current_furniture"])
        desired_furniture = st.text_area("Desired Furniture", sketch_data["desired_furniture"])
        special_considerations = st.text_area("Special Considerations", sketch_data["special_considerations"])
        style = st.text_input("Style Preference", sketch_data["style"])
        budget = st.text_input("Budget", sketch_data["budget"])

        submitted = st.form_submit_button("Generate AI Suggestions")

        if submitted:
            final_data = {
                "room_type": room_type,
                "dimensions": dimensions,
                "layout_notes": layout_notes,
                "current_furniture": current_furniture,
                "desired_furniture": desired_furniture,
                "special_considerations": special_considerations,
                "style": style,
                "budget": budget
            }

            with st.spinner("Talking to the AI..."):
                result = generate_layout_and_followup(final_data)

            st.success("Here's what the AI came up with:")
            st.markdown("### 📋 AI Output")
            st.markdown(result)

            # Save to notes
            add_note(selected_id, "AI", result)
            st.success("AI summary has been saved to client notes!")

else:
    st.info("Select a client above to begin.")
