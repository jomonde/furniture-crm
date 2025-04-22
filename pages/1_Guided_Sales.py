import streamlit as st
from db import add_client, get_all_clients_with_ids

st.set_page_config(page_title="Guided Sales Conversation", page_icon="🧭")

st.title("🧭 Guided Sales Experience")

st.markdown("Use this tool during live conversations to guide the guest and capture their needs in real time.")

with st.form("guided_sales_form"):
    st.subheader("👤 Guest Info")
    name = st.text_input("Full Name")
    contact = st.text_input("Phone or Email")
    room_focus = st.selectbox("What room are we working on first?", ["Living Room", "Bedroom", "Dining Room", "Office", "Outdoor", "Other"])

    st.subheader("🏠 Lifestyle & Use")
    who_uses = st.text_area("Who uses this space most? Any special routines or needs?")
    activities = st.text_area("Any daily activities you want this room to support?")
    vibe = st.text_area("How would you describe your ideal vibe for this space?")

    st.subheader("📏 Room Logistics")
    dimensions = st.text_input("Approximate Dimensions (e.g., 12x15 ft)")
    layout_notes = st.text_area("Describe layout: windows, doors, walkways, etc.")
    lighting = st.text_input("Describe lighting (natural or artificial)")

    st.subheader("🎨 Style & Function")
    style_pref = st.text_input("Preferred Style")
    must_haves = st.text_area("Must-haves or deal-breakers?")
    keeping = st.text_area("Any current furniture you're keeping?")

    st.subheader("🧸 Comfort & Budget")
    considerations = st.text_area("Special considerations (pets, kids, etc.)")
    storage = st.text_input("Storage needs?")
    budget = st.text_input("Budget range")

    st.subheader("🗒️ Internal Notes & Actions")
    notes = st.text_area("Salesperson notes (internal)")
    follow_up_flag = st.checkbox("Follow up in 48 hours with a layout plan")

    submitted = st.form_submit_button("Save Guest Profile")
    if submitted:
        add_client(name, contact, room_focus, style_pref, budget)
        st.success(f"Client profile for {name} saved!")

        # Optionally, log layout notes as a sketch (we can automate this later)
        st.info("Room sketch info can be added from the Room Sketch Helper section.")
