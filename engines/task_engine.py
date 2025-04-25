# task_engine.py

from datetime import date, datetime
from db import (
    get_active_clients,
    get_sales_by_client,
    get_last_task_date,
    add_task,
    get_client_by_id,
    get_room_sketches_by_client
)
from templates.followup_plan import FOLLOW_UP_PLANS
from engines.message_engine import generate_followup_message

def get_days_since_first_sale(sales):
    if not sales:
        return None
    first_sale = min(s["date"] for s in sales if s["status"] in ["Closed", "Open"])
    days = (date.today() - datetime.fromisoformat(first_sale).date()).days
    return days


def get_followup_type(client_data, sales):
    if not sales:
        return "shopper"
    days_since = get_days_since_first_sale(sales)
    return "long_term" if days_since and days_since >= 365 else "buyer"


def has_task_for_today(client_id, description):
    last_task_date = get_last_task_date(client_id)
    return last_task_date == date.today().isoformat()


def run_daily_task_generator():
    active_clients = get_active_clients()

    for client in active_clients:
        client_id = client["id"]
        sales = get_sales_by_client(client_id)
        client_data = get_client_by_id(client_id)
        sketches = get_room_sketches_by_client(client_id)
        latest_sketch = sketches[-1] if sketches else {}

        plan_type = get_followup_type(client, sales)
        plan = FOLLOW_UP_PLANS.get(plan_type, [])

        # --- 1. Client-Level Tasks ---
        client_days = get_days_since_first_sale(sales)
        if client_days:
            for step in plan:
                if step["days_after"] == client_days:
                    desc = step["description"]

                    if has_task_for_today(client_id, desc):
                        continue

                    message = generate_followup_message(
                        client_type=plan_type,
                        style="text",
                        client_data=client_data,
                        sketch_data=latest_sketch
                    )

                    add_task(client_id, desc, date.today().isoformat(), message=message, title=desc[:50])

        # --- 2. Sale-Level Tasks ---
        for sale in sales:
            if sale["status"] in ["Open", "Closed"]:
                sale_days = (date.today() - datetime.fromisoformat(sale["date"]).date()).days
                for step in plan:
                    if step["days_after"] == sale_days:
                        desc = f"{step['description']} (Order ${sale['amount']})"

                        if has_task_for_today(client_id, desc):  # prevent duplication
                            continue

                        message = generate_followup_message(
                            client_type=plan_type,
                            style="text",
                            client_data=client_data,
                            sketch_data=latest_sketch
                        )

                        add_task(client_id, desc, date.today().isoformat(), message, sale_id=sale["id"])
