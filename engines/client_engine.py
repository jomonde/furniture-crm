# client_engine.py

from db import (
    get_client_by_id,
    get_sales_by_client,
    get_tasks_by_client,
    get_notes_by_client,
    get_room_sketches_by_client
)
import streamlit as st
from openai import OpenAI
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def gather_client_history(client_id):
    client_info = get_client_by_id(client_id)
    sales = get_sales_by_client(client_id)
    tasks = get_tasks_by_client(client_id)
    notes = get_notes_by_client(client_id)
    sketches = get_room_sketches_by_client(client_id)

    return {
        "client": client_info,
        "sales": sales,
        "tasks": tasks,
        "notes": notes,
        "sketches": sketches
    }

def generate_client_summary(client_data):
    client_info = client_data.get("client", {})
    sales = client_data.get("sales", [])
    tasks = client_data.get("tasks", [])
    notes = client_data.get("notes", [])
    sketches = client_data.get("sketches", [])

    # Build input string
    prompt = f"""
You are a CRM assistant helping a furniture salesperson understand their client.

Based on the data below, create a clear summary of this client that includes:
- Their design and room preferences
- How they interact (communication style, engagement)
- Sales behavior (big spender? hesitant shopper?)
- Suggestions for next steps (follow-up, products, style cues)
- Preferred follow-up tone (text/email/casual/formal)

Only include what's supported by data, and write in a helpful, natural tone.

Client Info:
{json.dumps(client_info, indent=2)}

Sales:
{json.dumps(sales, indent=2)}

Tasks:
{json.dumps(tasks, indent=2)}

Notes:
{json.dumps(notes, indent=2)}

Sketches:
{json.dumps(sketches, indent=2)}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a smart CRM assistant that summarizes client profiles from their history."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=700,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()