from supabase import create_client
from datetime import (datetime, date)
import os
import streamlit as st

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ----------------------------
# CLIENTS
# ----------------------------

def add_client(name, phone, email, address, rooms, style, budget, status):
    if not (phone or email or address):
        raise ValueError("At least one of phone, email, or address is required.")
    response = supabase.table("clients").insert({
        "name": name,
        "phone": phone,
        "email": email,
        "address": address,
        "rooms": rooms,
        "style": style,
        "budget": budget,
        "status": status
    }).execute()
    return response

def get_all_clients_with_ids():
    response = supabase.table("clients").select("*").order("id", desc=False).execute()
    return response.data

def update_client(client_id, name, phone, email, address, rooms, style, budget, status):
    supabase.table("clients").update({
        "name": name,
        "phone": phone,
        "email": email,
        "address": address,
        "rooms": rooms,
        "style": style,
        "budget": budget,
        "status": status
    }).eq("id", client_id).execute()

def get_client_by_id(client_id):
    result = supabase.table("clients").select("*").eq("id", client_id).single().execute()
    return result.data

# ----------------------------
# ROOM SKETCHES
# ----------------------------

def add_room_sketch(client_id, room_type, dimensions, layout_notes, current_furniture, desired_furniture, special_considerations):
    supabase.table("room_sketches").insert({
        "client_id": client_id,
        "room_type": room_type,
        "dimensions": dimensions,
        "layout_notes": layout_notes,
        "current_furniture": current_furniture,
        "desired_furniture": desired_furniture,
        "special_considerations": special_considerations
    }).execute()

def get_room_sketches_by_client(client_id):
    response = supabase.table("room_sketches").select("*").eq("client_id", client_id).order("id", desc=False).execute()
    return response.data

# ----------------------------
# NOTES
# ----------------------------

def add_note(client_id, note_type, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    supabase.table("client_notes").insert({
        "client_id": client_id,
        "timestamp": timestamp,
        "type": note_type,
        "content": content
    }).execute()

def get_notes_by_client(client_id):
    response = supabase.table("client_notes").select("*").eq("client_id", client_id).order("timestamp", desc=True).execute()
    return response.data

def update_note(note_id, new_content):
    supabase.table("client_notes").update({
        "content": new_content
    }).eq("id", note_id).execute()

def delete_note(note_id):
    supabase.table("client_notes").delete().eq("id", note_id).execute()

def get_sales_by_client(client_id):
    response = supabase.table("sales").select("*").eq("client_id", client_id).order("date", desc=True).execute()
    return response.data

def update_sale(sale_id, amount, status, notes):
    supabase.table("sales").update({
        "amount": amount,
        "status": status,
        "notes": notes
    }).eq("id", sale_id).execute()

def void_sale(sale_id):
    supabase.table("sales").update({
        "status": "Void"
    }).eq("id", sale_id).execute()

def get_total_sales_volume_by_client(client_id):
    result = supabase.table("sales").select("amount").eq("client_id", client_id).eq("status", "Sold").execute()
    amounts = [s["amount"] for s in result.data if s["amount"] is not None]
    return round(sum(amounts), 2)

def get_average_sale_by_client(client_id):
    result = supabase.table("sales").select("amount").eq("client_id", client_id).eq("status", "Sold").execute()
    amounts = [s["amount"] for s in result.data if s["amount"] is not None]
    return round(sum(amounts) / len(amounts), 2) if amounts else 0.0

def get_first_sale_date_by_client(client_id):
    result = supabase.table("sales").select("date").eq("client_id", client_id).eq("status", "Sold").order("date", desc=False).limit(1).execute()
    if result.data:
        return result.data[0]["date"]
    return None

def get_average_days_between_sales(client_id):
    result = supabase.table("sales").select("date").eq("client_id", client_id).eq("status", "Sold").order("date", desc=False).execute()
    dates = [datetime.strptime(s["date"], "%Y-%m-%d") for s in result.data if s.get("date")]
    if len(dates) < 2:
        return None
    diffs = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    avg_days = sum(diffs) / len(diffs)
    return round(avg_days, 1)

# Add a new task to follow up
def add_task(client_id, description, due_date, title=None, message=None, sale_id=None):
    task_data = {
        "client_id": client_id,
        "description": description,
        "due_date": due_date,
        "completed": False,
        "title": title or description[:50],
        "message": message
    }

    if message:
        task_data["message"] = message
    if sale_id:
        task_data["sale_id"] = sale_id

    supabase.table("tasks").insert(task_data).execute()

# Get all tasks by specific client
def get_tasks_by_client(client_id):
    result = supabase.table("tasks") \
        .select("*") \
        .eq("client_id", client_id) \
        .order("due_date") \
        .execute()
    return result.data if result.data else []

# Get all tasks due on a specific date
def get_tasks_by_date(due_date):
    result = supabase.table("tasks").select("*").eq("due_date", due_date).execute()
    return result.data if result.data else []

# Mark a task as complete
def complete_task(task_id):
    """
    Marks a task as completed and updates the related client's last_contact timestamp.
    """
    # First, fetch the task to get the client_id
    task_response = supabase.table("tasks").select("*").eq("id", task_id).single().execute()
    task = task_response.data

    if not task:
        return False

    client_id = task.get("client_id")

    # Mark the task as completed
    supabase.table("tasks").update({"completed": True}).eq("id", task_id).execute()

    # Update client's last_contact to now
    if client_id:
        from datetime import datetime
        now = datetime.utcnow().isoformat()
        supabase.table("clients").update({"last_contact": now}).eq("id", client_id).execute()

    return True

def get_open_tasks():
    result = supabase.table("tasks") \
        .select("*") \
        .eq("completed", False) \
        .order("due_date") \
        .execute()
    return result.data if result.data else []

def get_overdue_tasks():
    today = date.today().isoformat()
    result = supabase.table("tasks") \
        .select("*") \
        .lt("due_date", today) \
        .eq("completed", False) \
        .order("due_date") \
        .execute()
    return result.data if result.data else []

def get_active_clients():
    result = supabase.table("clients") \
        .select("*") \
        .eq("status", "Active") \
        .order("name") \
        .execute()
    return result.data if result.data else []

def get_last_task_date(client_id):
    result = supabase.table("tasks") \
        .select("due_date") \
        .eq("client_id", client_id) \
        .order("due_date", desc=True) \
        .limit(1) \
        .execute()

    if result.data and len(result.data) > 0:
        return result.data[0]["due_date"]
    return None

def get_client_id(name=None, phone=None):
    """
    Get a client ID by name, phone, or both. Returns None if not found.
    """
    if not name and not phone:
        return None

    query = supabase.table("clients").select("id")

    if name and phone:
        query = query.eq("name", name).eq("phone", phone)
    elif name:
        query = query.eq("name", name)
    elif phone:
        query = query.eq("phone", phone)

    response = query.execute()
    data = response.data

    if data and len(data) > 0:
        return data[0]["id"]
    return None

def update_client_summary(client_id, summary_text):
    supabase.table("clients").update({
        "client_summary": summary_text,
        "summary_last_updated": datetime.utcnow().isoformat()
    }).eq("id", client_id).execute()


def compute_client_last_modified(client_id):
    """
    Calculate the latest modification timestamp for a client based on client info, notes, sketches, sales, and tasks.
    """

    # 1. Pull client core info
    client = get_client_by_id(client_id)
    timestamps = []

    if client and client.get("updated_at"):
        timestamps.append(client["updated_at"])

    # 2. Pull notes timestamps
    notes = get_notes_by_client(client_id)
    for note in notes:
        if note.get("timestamp"):
            timestamps.append(note["timestamp"])

    # 3. Pull sketches timestamps
    sketches = get_room_sketches_by_client(client_id)
    for sketch in sketches:
        if sketch.get("created_at"):
            timestamps.append(sketch["created_at"])

    # 4. Pull sales timestamps
    sales = get_sales_by_client(client_id)
    for sale in sales:
        if sale.get("date"):
            timestamps.append(sale["date"])

    # 5. Pull tasks timestamps
    tasks = get_tasks_by_client(client_id)
    for task in tasks:
        if task.get("due_date"):
            timestamps.append(task["due_date"])

    if not timestamps:
        return None  # No data available

    # Convert all timestamps to datetime objects
    datetime_stamps = []
    for ts in timestamps:
        try:
            datetime_stamps.append(datetime.fromisoformat(ts))
        except Exception:
            pass  # Skip any invalid timestamp formats

    if not datetime_stamps:
        return None

    # Return the latest timestamp
    latest_timestamp = max(datetime_stamps)
    return latest_timestamp.isoformat()

def get_all_tasks():
    """
    Pulls all tasks from the database.
    """
    response = supabase.table("tasks").select("*").execute()
    if response.data:
        return response.data
    return []

def get_all_sales():
    """
    Pulls all sales records from the database.
    """
    response = supabase.table("sales").select("*").execute()
    if response.data:
        return response.data
    return []

def update_last_contact(client_id):
    """
    Updates the last_contact field for a client to now().
    """
    from datetime import datetime
    now = datetime.utcnow().isoformat()

    supabase.table("clients").update({"last_contact": now}).eq("id", client_id).execute()

def add_sale(client_id, amount, status, sale_date, notes=""):
    """
    Adds a new sale record to the database.
    """
    sale_data = {
        "client_id": client_id,
        "amount": amount,
        "status": status,
        "date": sale_date,
        "notes": notes
    }
    supabase.table("sales").insert(sale_data).execute()

def gather_client_history(client_id):
    """
    Gathers complete client profile data, notes, sketches, sales, and tasks.
    Useful for generating AI summaries and smarter follow-ups.
    """

    client_info = get_client_by_id(client_id)
    sketches = get_room_sketches_by_client(client_id)
    notes = get_notes_by_client(client_id)
    sales = get_sales_by_client(client_id)
    tasks = get_tasks_by_client(client_id)

    history = {
        "info": client_info,
        "sketches": sketches,
        "notes": notes,
        "sales": sales,
        "tasks": tasks
    }

    return history
