import streamlit as st
from datetime import date, datetime
from db import get_all_tasks, complete_task, get_client_by_id

# --- Page Setup ---
st.set_page_config(page_title="Tasks", page_icon="📋", layout="wide")
st.title("📋 The Task Manager")

# --- Fetch Tasks ---
tasks = get_all_tasks()

# Separate tasks
today = date.today().isoformat()

open_tasks = [t for t in tasks if not t["completed"]]
completed_tasks = [t for t in tasks if t["completed"]]

overdue_tasks = [t for t in open_tasks if t["due_date"] < today]
today_tasks = [t for t in open_tasks if t["due_date"] == today]
upcoming_tasks = [t for t in open_tasks if t["due_date"] > today]

# --- Today's Tasks ---
st.subheader("🟡 Tasks Due Today")

if today_tasks:
    for task in today_tasks:
        client_info = get_client_by_id(task["client_id"])
        client_name = client_info["name"] if client_info else "Unknown Client"

        with st.container():
            st.markdown(f"**{task['description']}** — {client_name}")
            if task.get("message"):
                st.caption(f"💬 {task['message']}")
            if st.checkbox(f"Mark Done", key=f"today_task_{task['id']}"):
                complete_task(task["id"])
                st.success("Task marked complete.")
                st.rerun()
else:
    st.info("🎉 No tasks due today!")

# --- Upcoming Tasks ---
st.subheader("🟢 Upcoming Tasks")

if upcoming_tasks:
    for task in upcoming_tasks:
        client_info = get_client_by_id(task["client_id"])
        client_name = client_info["name"] if client_info else "Unknown Client"

        with st.container():
            st.markdown(f"**{task['description']}** — Due {task['due_date']} — {client_name}")
            if st.checkbox(f"Mark Done", key=f"upcoming_task_{task['id']}"):
                complete_task(task["id"])
                st.success("Task marked complete.")
                st.rerun()
else:
    st.info("No upcoming tasks.")

# --- Overdue Tasks ---
st.subheader("🔴 Overdue Tasks")

if overdue_tasks:
    for task in overdue_tasks:
        client_info = get_client_by_id(task["client_id"])
        client_name = client_info["name"] if client_info else "Unknown Client"

        with st.container():
            st.markdown(f"**{task['description']}** — Overdue since {task['due_date']} — {client_name}")
            if st.checkbox(f"Mark Done", key=f"overdue_task_{task['id']}"):
                complete_task(task["id"])
                st.success("Task marked complete.")
                st.rerun()
else:
    st.success("No overdue tasks! 🔥")

# --- Completed Tasks ---
with st.expander("✅ Completed Tasks (Click to View)"):
    if completed_tasks:
        for task in completed_tasks[::-1]:  # show most recent completed first
            client_info = get_client_by_id(task["client_id"])
            client_name = client_info["name"] if client_info else "Unknown Client"

            st.markdown(f"- {task['description']} — Done for {client_name} on {task['due_date']}")
    else:
        st.info("No completed tasks yet.")
