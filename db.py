from supabase import create_client
from datetime import datetime
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ----------------------------
# CLIENTS
# ----------------------------

def add_client(name, phone, email, address, rooms, style, budget):
    if not (phone or email or address):
        raise ValueError("At least one of phone, email, or address is required.")
    response = supabase.table("clients").insert({
        "name": name,
        "phone": phone,
        "email": email,
        "address": address,
        "rooms": rooms,
        "style": style,
        "budget": budget
    }).execute()
    return response

def get_all_clients_with_ids():
    response = supabase.table("clients").select("*").order("id", desc=False).execute()
    return response.data

def update_client(client_id, name, phone, email, address, rooms, style, budget):
    supabase.table("clients").update({
        "name": name,
        "phone": phone,
        "email": email,
        "address": address,
        "rooms": rooms,
        "style": style,
        "budget": budget
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
def add_task(client_id, description, due_date):
    supabase.table("tasks").insert({
        "client_id": client_id,
        "description": description,
        "due_date": due_date,
        "completed": False
    }).execute()

# Get all tasks due on a specific date
def get_tasks_by_date(due_date):
    result = supabase.table("tasks").select("*").eq("due_date", due_date).execute()
    return result.data if result.data else []

# Mark a task as complete
def complete_task(task_id):
    supabase.table("tasks").update({"completed": True}).eq("id", task_id).execute()