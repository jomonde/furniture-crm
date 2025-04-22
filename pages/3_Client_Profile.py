import streamlit as st
from db import (
    get_all_clients_with_ids,
    get_room_sketches_by_client,
    get_notes_by_client,
    update_note,
    delete_note
)

st.set_page_config(page_title="Client Profile", page_icon="📇")
st.title("📇 Client Profile")

# Load clients
clients = get_all_clients_with_ids()
client_options = {f"{name} ({contact})": cid for cid, name, contact, *_ in clients}
client_display = st.selectbox("Select a client to view details", ["-- Select Client --"] + list(client_options.keys()))

if client_display != "-- Select Client --":
    selected_id = client_options[client_display]
    client_data = next((c for c in clients if c[0] == selected_id), None)

    if client_data:
        client_id, name, contact, rooms, style, budget = client_data

        st.markdown(f"### 👤 {name}")
        st.markdown(f"**Contact:** {contact}")
        st.markdown(f"**Room Focus:** {rooms}")
        st.markdown(f"**Style Preference:** {style}")
        st.markdown(f"**Budget:** {budget}")

        # Room Sketches
        sketches = get_room_sketches_by_client(selected_id)
        if sketches:
            st.subheader("📐 Room Sketches")
            for i, sketch in enumerate(sketches, 1):
                st.markdown(f"**Sketch #{i} – {sketch[0]}**")
                st.markdown(f"""
                - **Dimensions:** {sketch[1]}
                - **Layout Notes:** {sketch[2]}
                - **Current Furniture:** {sketch[3]}
                - **Desired Furniture:** {sketch[4]}
                - **Special Considerations:** {sketch[5]}
                """)
        else:
            st.info("No sketches found for this client.")

        # Notes Section
        st.subheader("🗒️ Notes")
        notes = get_notes_by_client(selected_id)

        if notes:
            for note_id, timestamp, note_type, content in notes:
                with st.expander(f"🕒 {timestamp} | 🏷️ {note_type}"):
                    edited_note = st.text_area("Edit Note", content, key=f"edit_{note_id}")
                    col1, col2 = st.columns(2)
                    if col1.button("💾 Save", key=f"save_{note_id}"):
                        update_note(note_id, edited_note)
                        st.success("Note updated!")
                        st.experimental_rerun()

                    if col2.button("🗑️ Delete", key=f"delete_{note_id}"):
                        delete_note(note_id)
                        st.warning("Note deleted.")
                        st.experimental_rerun()
        else:
            st.info("No notes available for this client.")
