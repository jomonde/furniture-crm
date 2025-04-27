import streamlit as st
from db import get_all_sales, get_client_by_id

# --- Page Setup ---
st.set_page_config(page_title="Sales", page_icon="📦", layout="wide")
st.title("📦 Sales Tracker")

# --- Fetch Sales ---
sales = get_all_sales()

# --- Organize Sales ---
open_sales = [s for s in sales if s["status"] == "Open"]
closed_sales = [s for s in sales if s["status"] == "Closed"]
unsold_sales = [s for s in sales if s["status"] in ["Unsold", "Void"]]

# --- Add a Sale ---
st.subheader("➕ Add New Sale")
from components.sale_form import sale_entry_form  # Adjust path if needed
sale_entry_form()

# --- KPIs ---
st.subheader("📊 Sales Overview")

total_volume = sum(float(s["amount"]) for s in closed_sales)
average_sale = (total_volume / len(closed_sales)) if closed_sales else 0

col1, col2, col3 = st.columns(3)

col1.metric("Open Sales", len(open_sales))
col2.metric("Closed Sales", len(closed_sales))
col3.metric("Total Sales Volume", f"${total_volume:,.2f}")

st.metric("Average Closed Sale", f"${average_sale:,.2f}")

# --- Open Sales ---
with st.expander("🟡 Open Sales"):
    if open_sales:
        for sale in open_sales:
            client_info = get_client_by_id(sale["client_id"])
            client_name = client_info["name"] if client_info else "Unknown Client"

            st.markdown(f"**{client_name}** — ${sale['amount']} — Open since {sale['date'][:10]}")
            st.caption(f"Notes: {sale.get('notes', '-')}")
    else:
        st.info("No open sales.")

# --- Closed Sales ---
with st.expander("✅ Closed Sales"):
    if closed_sales:
        for sale in closed_sales:
            client_info = get_client_by_id(sale["client_id"])
            client_name = client_info["name"] if client_info else "Unknown Client"

            st.markdown(f"**{client_name}** — ${sale['amount']} — Closed on {sale['date'][:10]}")
            st.caption(f"Notes: {sale.get('notes', '-')}")
    else:
        st.info("No closed sales.")

# --- Unsold or Voided Sales ---
with st.expander("❌ Unsold / Voided Sales"):
    if unsold_sales:
        for sale in unsold_sales:
            client_info = get_client_by_id(sale["client_id"])
            client_name = client_info["name"] if client_info else "Unknown Client"

            st.markdown(f"**{client_name}** — ${sale['amount']} — {sale['status']} — {sale['date'][:10]}")
            st.caption(f"Notes: {sale.get('notes', '-')}")
    else:
        st.success("No unsold or voided sales — good work! 🎉")
