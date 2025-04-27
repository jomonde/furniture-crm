from db import (
    get_tasks_by_client,
    get_all_clients_with_ids,
    get_sales_by_client,
    get_all_sales
)
from datetime import date, datetime

# 1️⃣ Today's Open Tasks
def get_open_tasks(due_today=False):
    """
    Returns a list of open tasks.
    If due_today=True, filters tasks due today only.
    """
    from db import get_all_tasks  # You should have a global get_all_tasks()
    tasks = get_all_tasks()

    open_tasks = [t for t in tasks if not t["completed"]]

    if due_today:
        today_str = date.today().isoformat()
        open_tasks = [t for t in open_tasks if t["due_date"] == today_str]

    return sorted(open_tasks, key=lambda x: x["due_date"])

# 2️⃣ High Priority Clients
def get_high_priority_clients():
    """
    Returns clients that are New Leads, Engaged, or Buyers.
    Prioritized by last contact date.
    """
    clients = get_all_clients_with_ids()
    high_priority = [c for c in clients if c["status"] == "active" and c.get("lifecycle_stage", "New Lead") in ["New Lead", "Engaged", "Buyer"]]

    # Sort by last contact if available
    def get_last_contact(c):
        return datetime.fromisoformat(c.get("last_contact", "1900-01-01T00:00:00"))

    high_priority = sorted(high_priority, key=get_last_contact)

    return high_priority

# 3️⃣ Sales Pipeline Data
def get_sales_pipeline_data():
    """
    Returns snapshot data for sales pipeline: open, closed, unsold, and total sales volume.
    """
    sales = get_all_sales()

    open_sales = sum(1 for s in sales if s["status"] == "Open")
    closed_sales = sum(1 for s in sales if s["status"] == "Closed")
    unsold_sales = sum(1 for s in sales if s["status"] == "Unsold")
    total_volume = sum(float(s["amount"]) for s in sales if s["status"] == "Closed")

    return {
        "open": open_sales,
        "closed": closed_sales,
        "unsold": unsold_sales,
        "total_volume": total_volume
    }

# 4️⃣ Insights and Suggestions
def get_insights_suggestions():
    """
    Returns a list of smart insights or suggestions for today.
    Example: Clients not contacted in 14+ days.
    """
    clients = get_all_clients_with_ids()
    suggestions = []

    today = datetime.today()

    for client in clients:
        last_contact_str = client.get("last_contact")
        if last_contact_str:
            try:
                last_contact = datetime.fromisoformat(last_contact_str)
                days_since = (today - last_contact).days
                if days_since >= 14 and client["status"] == "active":
                    suggestions.append(f"Reach out to {client['name']} — no contact in {days_since} days.")
            except Exception:
                pass  # skip invalid dates

    return suggestions
