import streamlit as st
from db import (
    get_all_clients_with_ids,
    get_client_by_id,
    add_client,
    add_sale,
    get_all_sales,
    update_sale
)
from datetime import date

# --- Page Setup ---
st.set_page_config(page_title="Order Book", page_icon="📦", layout="wide")
st.title("📦 Order Book 2.0")

# --- Sales Viewer Section ---
st.header("📋 Sales Overview")

sales = get_all_sales()

# Organize by Status
open_sales = [s for s in sales if s["status"] == "Open"]
closed_sales = [s for s in sales if s["status"] == "Closed"]
voided_sales = [s for s in sales if s["status"] in ["Void", "Unsold"]]

def display_sales_list(title, sale_list):
    with st.expander(f"{title} ({len(sale_list)})", expanded=True if title == "Open Sales" else False):
        if sale_list:
            for sale in sale_list:
                client_info = get_client_by_id(sale["client_id"])
                client_name = client_info["name"] if client_info else "Unknown Client"

                st.divider()

                # --- Sale Quick Overview ---
                st.markdown(f"**{client_name}** — ${sale['amount']} — {sale['status']} — {sale['date'][:10]}")
                st.caption(f"Notes: {sale.get('notes', '-')}")
                
                # --- Quick Status Change Buttons ---
                col1, col2, col3 = st.columns(3)
                if col1.button("🔘 Open", key=f"open_{sale['id']}"):
                    update_sale(sale["id"], sale["amount"], "Open", sale.get("notes", ""))
                    st.success("Sale marked Open!")
                    st.rerun()
                if col2.button("✅ Close", key=f"close_{sale['id']}"):
                    update_sale(sale["id"], sale["amount"], "Closed", sale.get("notes", ""))
                    st.success("Sale Closed!")
                    st.rerun()
                if col3.button("❌ Void", key=f"void_{sale['id']}"):
                    update_sale(sale["id"], sale["amount"], "Void", sale.get("notes", ""))
                    st.success("Sale Voided!")
                    st.rerun()

                # --- Inline Edit Form (no nesting) ---
                with st.form(f"edit_sale_form_{sale['id']}", clear_on_submit=False):
                    new_amount = st.number_input("Amount", value=float(sale["amount"]), step=50.0, key=f"amount_{sale['id']}")
                    new_status = st.selectbox(
                        "Status",
                        ["Open", "Closed", "Void", "Unsold"],
                        index=["Open", "Closed", "Void", "Unsold"].index(sale["status"]),
                        key=f"status_{sale['id']}"
                    )
                    new_notes = st.text_area("Notes", value=sale.get("notes", ""), key=f"notes_{sale['id']}")
                    update = st.form_submit_button("💾 Update Sale")

                    if update:
                        update_sale(sale["id"], new_amount, new_status, new_notes)
                        st.success("Sale updated!")
                        st.rerun()
        else:
            st.info(f"No {title.lower()} yet.")

# Display sales lists
display_sales_list("Open Sales", open_sales)
display_sales_list("Closed Sales", closed_sales)
display_sales_list("Voided/Unsold Sales", voided_sales)

# --- Order Writer Section ---
st.header("➕ Create New Sale Ticket")

# Client Selection or Add
clients = get_all_clients_with_ids()
client_options = {f"{c['name']} ({c['phone']})": c["id"] for c in clients}
client_options["➕ Add New Client"] = "new"

selected_client_label = st.selectbox("Select Existing Client or Add New", list(client_options.keys()))

if selected_client_label == "➕ Add New Client":
    st.subheader("➕ Add New Client")

    with st.form("add_client_form"):
        name = st.text_input("Full Name")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        address = st.text_input("Address")
        rooms = st.text_input("Room(s) of Interest")
        style = st.text_input("Style Preference")
        budget = st.text_input("Budget")
        status = st.selectbox("Status", ["active", "inactive"])

        save_client = st.form_submit_button("Save New Client")

        if save_client:
            if not name.strip():
                st.warning("Name is required.")
            else:
                add_client(name, phone, email, address, rooms, style, budget, status)
                st.success(f"Client {name} added!")
                st.rerun()

else:
    # Create Sale Ticket
    selected_client_id = client_options[selected_client_label]

    with st.form("create_sale_form", clear_on_submit=True):
        amount = st.number_input("Sale Amount ($)", min_value=0.0, step=50.0)
        status = st.selectbox("Sale Status", ["Open", "Closed", "Unsold", "Void"], index=0)
        notes = st.text_area("Notes (optional)")

        create_sale = st.form_submit_button("💾 Create Sale Ticket")

        if create_sale:
            sale_date = date.today().isoformat()
            add_sale(selected_client_id, amount, status, sale_date, notes)
            st.success("✅ Sale Ticket Created!")
            st.rerun()
