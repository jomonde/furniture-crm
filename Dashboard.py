import streamlit as st
from datetime import date
from db_dashboard import (
    get_total_clients,
    get_clients_by_status,
    get_total_sales_volume,
    get_average_sale,
    get_close_rate,
    get_tasks,
    add_task
)

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
# DAILY TASKS / REMINDERS
# -------------------------------
st.markdown("---")
st.subheader("📝 Reminders & Daily Tasks")

tasks = get_tasks()

with st.form("task_form", clear_on_submit=True):
    task_title = st.text_input("Task")
    task_due = st.date_input("Due Date", value=date.today())
    submitted = st.form_submit_button("Add Task")
    if submitted:
        add_task(task_title, task_due)
        st.success("Task added!")
        st.rerun()

for task in tasks:
    status = "✅" if task["completed"] else "⬜"
    due = task["due_date"]
    st.markdown(f"- {status} **{task['title']}** — due {due}")

# -------------------------------
# PERFORMANCE SNAPSHOT
# -------------------------------
st.markdown("---")
st.subheader("📅 Performance Snapshot")

month = st.selectbox("View Month", ["January", "February", "March", "April", "May"])
st.markdown("_(Calendar view + historical data coming soon...)_")
st.info(f"Showing snapshot for **{month}** — real data view in development.")
