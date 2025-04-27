import streamlit as st
from db import add_sale

def sale_entry_form(selected_client_id=None):
    """
    Form to create a new sale. Can be used in Sales Page, Client Profile, or Dashboard.
    If selected_client_id is provided, pre-fill client ID.
    """

    with st.form("add_sale_form", clear_on_submit=True):
        amount = st.number_input("Sale Amount ($)", min_value=0.0, step=50.0)
        status = st.selectbox("Sale Status", ["Open", "Closed", "Unsold", "Void"])
        notes = st.text_area("Sale Notes (optional)")
        
        if not selected_client_id:
            client_id = st.text_input("Client ID")  # Free text if no client selected
        else:
            client_id = selected_client_id

        submit = st.form_submit_button("💾 Save Sale")

        if submit:
            if not client_id:
                st.warning("Client ID is required to record a sale.")
            else:
                from datetime import date
                sale_date = date.today().isoformat()

                add_sale(client_id, amount, status, sale_date, notes)
                st.success("✅ Sale recorded successfully!")
                st.experimental_rerun()
