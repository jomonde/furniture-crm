import streamlit as st
from datetime import date
from db_dashboard import (
    get_open_tasks,
    get_high_priority_clients,
    get_sales_pipeline_data,
    get_insights_suggestions
)
from engines.task_engine import run_daily_task_generator

# --- Page setup ---
st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
st.title("🏠 Furniture CRM 2.0 Dashboard")

# --- Run the task engine automatically ---
if "task_engine_ran" not in st.session_state:
    run_daily_task_generator()
    st.session_state.task_engine_ran = True

# --- Add a Sale ---
with st.expander("➕ Quick Add Sale"):
    from components.sale_form import sale_entry_form
    sale_entry_form()

# --- Dashboard Layout ---
col1, col2 = st.columns(2)

# ---------------------------
# 📋 Today's Tasks
# ---------------------------
with col1:
    st.subheader("📋 Today's Tasks")

    tasks = get_open_tasks(due_today=True)

    if tasks:
        for task in tasks:
            with st.container():
                st.markdown(f"**{task['description']}** — Due {task['due_date']}")
                if task.get("message"):
                    st.caption(f"💬 {task['message']}")
                if st.button(f"✅ Mark Complete", key=f"complete_task_{task['id']}"):
                    from db import complete_task
                    complete_task(task["id"])
                    st.success("Task completed!")
                    st.rerun()
    else:
        st.success("🎉 No tasks due today!")

    if st.button("📋 View All Tasks"):
        st.switch_page("pages/2_Tasks.py")  # adjust the path as needed

    # --- NEW: Follow-Up Tasks Section ---
    st.subheader("✉️ Active Follow-Up Tasks")

    # Pull tasks
    from db import get_all_tasks, complete_task

    tasks = get_all_tasks()
    open_followup_tasks = [t for t in tasks if not t["completed"] and t.get("message")]

    if open_followup_tasks:
        for task in open_followup_tasks:
            from db import get_client_by_id
            client_info = get_client_by_id(task["client_id"])
            client_name = client_info["name"] if client_info else "Unknown Client"

            with st.container():
                st.markdown(f"**{task['description']}** — {client_name} (Due {task['due_date']})")
                st.caption(f"💬 {task['message']}")
                if st.checkbox(f"Mark Done", key=f"followup_task_{task['id']}"):
                    complete_task(task["id"])
                    st.success("Task completed!")
                    st.experimental_rerun()
    else:
        st.info("No active follow-up tasks right now.")

# ---------------------------
# 🛋️ Hot Clients
# ---------------------------
with col2:
    st.subheader("🛋️ Hot Clients")

    hot_clients = get_high_priority_clients()

    if hot_clients:
        for client in hot_clients:
            with st.container():
                st.markdown(f"**{client['name']}** — {client['lifecycle_stage']}")
                st.caption(f"Next Action: {client.get('next_action', 'Follow up')}")
                st.caption(f"Last Contact: {client.get('last_contact', 'Unknown')}")
    else:
        st.info("No high-priority clients right now.")

    if st.button("👥 View All Clients"):
        st.switch_page("pages/1_Clients.py")  # adjust the path as needed

# ---------------------------
# 📈 Sales Pipeline Snapshot
# ---------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("📈 Sales Pipeline")

    sales_data = get_sales_pipeline_data()

    st.metric("Open Sales", sales_data["open"])
    st.metric("Closed Sales", sales_data["closed"])
    st.metric("Unsold Leads", sales_data["unsold"])
    st.metric("Sales Volume (This Month)", f"${sales_data['total_volume']:,.2f}")

    if st.button("📦 View Sales Report"):
        st.switch_page("pages/3_Sales.py")  # adjust the path as needed

# ---------------------------
# 🧠 Insights & Suggestions
# ---------------------------
with col4:
    st.subheader("🧠 Insights & Suggestions")

    insights = get_insights_suggestions()

    if insights:
        for suggestion in insights:
            st.markdown(f"✅ {suggestion}")
    else:
        st.info("No insights to suggest right now.")

    if st.button("🧠 Go to Insights"):
        st.switch_page("pages/4_Insights.py")  # future page if needed