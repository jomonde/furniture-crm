from supabase import create_client
import os
from datetime import datetime

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# ----------- CLIENT METRICS ------------ #

def get_total_clients():
    result = supabase.table("clients").select("id").execute()
    return len(result.data)

def get_clients_by_status(status):
    result = supabase.table("sales").select("client_id", "status").eq("status", status).execute()
    unique_clients = {s["client_id"] for s in result.data}
    return len(result.data)

# ----------- SALES METRICS ------------ #

def get_total_sales_volume():
    result = supabase.table("sales").select("amount").execute()
    amounts = [s["amount"] for s in result.data if s["amount"] is not None]
    return round(sum(amounts), 2)

def get_average_sale():
    result = supabase.table("sales").select("amount").execute()
    amounts = [s["amount"] for s in result.data if s["amount"] is not None]
    return round(sum(amounts) / len(amounts), 2) if amounts else 0.0

def get_close_rate():
    sold = get_clients_by_status("Sold")
    unsold = get_clients_by_status("Unsold")
    total = sold + unsold
    return round((sold / total) * 100, 1) if total > 0 else 0.0

# ----------- TASKS ------------ #

def get_tasks():
    result = supabase.table("tasks").select("*").order("due_date", desc=False).execute()
    return result.data

def add_task(title, due_date):
    supabase.table("tasks").insert({
        "title": title,
        "due_date": due_date.isoformat(),
        "completed": False,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
