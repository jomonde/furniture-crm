import streamlit as st
from datetime import date

# --- Engines ---
from engines.task_engine import run_daily_task_generator 

# --- DB Access ---
from db import (
    add_client,
    get_open_tasks,
    get_overdue_tasks,
    complete_task
)

from db_dashboard import (
    get_total_clients,
    get_clients_by_status,
    get_total_sales_volume,
    get_average_sale,
    get_close_rate,
    get_tasks, 
    add_task,
)

# --- Run the task engine automatically ---
if "task_engine_ran" not in st.session_state:
    run_daily_task_generator()
    st.session_state.task_engine_ran = True

# --- Page setup ---
st.set_page_config(page_title="Dashboard", page_icon="📊")
st.title("📊 Sales Dashboard")

# -------------------------------
# METRICS ROW
# -------------------------------
st.subheader("📈 Monthly Metrics Overview")

total_clients = get_total_clients()
clients_open = get_clients_by_status("Open")
clients_closed = get_clients_by_status("Closed")
total_sales_volume = get_total_sales_volume()
average_sale = get_average_sale()
close_rate = get_close_rate()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Clients", total_clients)
col2.metric("Close Rate", f"{close_rate}%")
col3.metric("Avg Sale", f"${average_sale:,.2f}")
col4.metric("Sales Volume", f"${total_sales_volume:,.2f}")

# -------------------------------
# PIPELINE SUMMARY
# -------------------------------
st.markdown("---")
st.subheader("🛠️ Pipeline Overview")

voided_invoices = get_clients_by_status("Void")
clients_unsold = get_clients_by_status("Unsold")

col5, col6, col7, col8 = st.columns(4)
col5.metric("Clients Open", clients_open)
col6.metric("Clients Closed", clients_closed)
col7.metric("Voided Invoices", voided_invoices)
col8.metric("Clients Unsold", clients_unsold)

# -------------------------------
# ADD NEW CLIENT
# -------------------------------
if st.checkbox("➕ Add a New Client"):
    with st.form("add_client_form", clear_on_submit=True):
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        address = st.text_input("Home Address")
        rooms = st.text_input("Room(s) of Interest (e.g. Living, Bedroom)")
        style = st.text_input("Style Preference")
        budget = st.text_input("Estimated Budget")

        submitted = st.form_submit_button("Save Client")

        if submitted:
            if not name.strip():
                st.warning("Name is required.")
            elif not (phone.strip() or email.strip() or address.strip()):
                st.warning("At least one contact method (phone, email, or address) is required.")
            else:
                add_client(name, phone, email, address, rooms, style, budget)
                st.success("Client added successfully!")

# -------------------------------
# DAILY TASKS / REMINDERS
# -------------------------------
st.subheader("✅ Tasks Overview")

open_tasks = get_open_tasks()
overdue_tasks = get_overdue_tasks()

# 🔴 Overdue tasks
if overdue_tasks:
    st.markdown("### 🔴 Overdue Tasks")
    for task in overdue_tasks:
        label = f"{task['description']} (Client ID {task['client_id']}) — due {task['due_date']}"
        if task.get("message"):
            st.markdown(f"*💬 Suggested:* {task['message']}")
        if st.checkbox(label, key=f"overdue_{task['id']}"):
            complete_task(task["id"])
            st.success("Overdue task completed.")
            st.rerun()
else:
    st.info("✅ No overdue tasks!")
# 🟡 Tasks Due Today
if open_tasks:
    st.markdown("### 🟡 Tasks Due Today & Open")
    for task in open_tasks:
        label = f"{task['description']} (Client ID {task['client_id']}) — due {task['due_date']}"
        if task.get("message"):
            st.markdown(f"*💬 Suggested Message:*\n{task['message']}")
        if st.checkbox(label, key=f"open_{task['id']}"):
            complete_task(task["id"])
            st.success("Task marked as complete.")
            st.rerun()
else:
    st.info("No open tasks scheduled.")

# -------------------------------
# PERFORMANCE SNAPSHOT
# -------------------------------
st.markdown("---")
st.subheader("📅 Performance Snapshot")

month = st.selectbox("View Month", ["January", "February", "March", "April", "May"])
st.markdown("_(Calendar view + historical data coming soon...)_")
st.info(f"Showing snapshot for **{month}** — real data view in development.")
