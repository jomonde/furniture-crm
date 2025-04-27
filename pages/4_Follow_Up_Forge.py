import streamlit as st
from datetime import date
from db import (
    get_all_clients_with_ids,
    get_client_by_id,
    gather_client_history,
    get_room_sketches_by_client,
    add_note,
    update_last_contact
)
from engines.message_engine import generate_followup_message

# --- Page Setup ---
st.set_page_config(page_title="Follow-Up Forge", page_icon="✉️", layout="wide")
st.title("✉️ Follow-Up Forge 2.1")

# --- Client Selection ---
clients = get_all_clients_with_ids()
client_options = {f"{c['name']} ({c['phone']})": c["id"] for c in clients}

search_term = st.text_input("🔍 Search for Client (name or phone)")
filtered_clients = [label for label in client_options if search_term.lower() in label.lower()]
selected_client_label = st.selectbox("Select Client", filtered_clients if filtered_clients else ["No matches found"])

if selected_client_label != "No matches found":
    selected_client_id = client_options[selected_client_label]
    client_info = get_client_by_id(selected_client_id)

    st.subheader("🛠️ Message Settings")

    # Detect client lifecycle stage
    lifecycle_stage = client_info.get("lifecycle_stage", "New Lead")
    st.markdown(f"**Client Stage Detected:** {lifecycle_stage}")

    # Choose Follow-Up Focus
    followup_type = st.selectbox(
        "Follow-Up Type",
        ["Specific Product Inquiry", "Post-Purchase Check-In", "Friendly General Check-In"]
    )

    message_style = st.selectbox("Message Style", ["text", "phone", "email", "handwritten"])
    custom_prompt = st.text_input("Optional Custom Add-On (e.g., mention a specific product, event)")

    if st.button("🧠 Generate Message"):
        with st.spinner("Crafting personalized message..."):
            client_history = gather_client_history(selected_client_id)
            sketches = get_room_sketches_by_client(selected_client_id)
            latest_sketch = sketches[-1] if sketches else {}

            generated_message = generate_followup_message(
                lifecycle_stage=lifecycle_stage,
                followup_type=followup_type,
                message_style=message_style,
                client_data=client_history,
                sketch_data=latest_sketch,
                custom_prompt=custom_prompt
            )

            if generated_message:
                st.success("Message Generated!")
                st.text_area("📝 Message Preview", generated_message, height=250, key="preview_message")

                if st.button("💾 Save Message to Client"):
                    add_note(selected_client_id, message_style.capitalize(), generated_message)
                    update_last_contact(selected_client_id)
                    st.success("✅ Message saved and last contact updated!")
                    st.rerun()
            else:
                st.error("Failed to generate a message. Try again.")
            
            if st.button("💾 Save Message to Client"):
                add_note(selected_client_id, message_style.capitalize(), generated_message)
                update_last_contact(selected_client_id)
                st.success("✅ Message saved and last contact updated!")

                # Prompt to add related task
                with st.expander("➕ Create Related Follow-Up Task"):
                    st.markdown("Optional: Schedule a follow-up task based on this message.")

                    followup_description = st.text_input("Task Description (e.g., 'Call to check in after email')")
                    followup_due_date = st.date_input("Task Due Date")

                    if st.button("📋 Save Task"):
                        from db import add_task  # Ensure you have add_task in db.py
                        today = date.today().isoformat()

                        # Quick task creation
                        add_task(
                            client_id=selected_client_id,
                            desc=followup_description,
                            due_date=followup_due_date.isoformat(),
                            message=generated_message,  # include message as context
                            title=followup_description[:50]
                        )

                        st.success("✅ Follow-up task created!")
                        st.rerun()


else:
    st.info("Select a client to begin follow-up generation.")
