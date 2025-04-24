from openai import OpenAI
import os
import json
import streamlit as st
from templates.followups import FOLLOW_UP_MESSAGES
from templates.followup_tones import FOLLOW_UP_TONES

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_layout_and_followup(sketch_data):
    prompt = f"""
    A customer is furnishing a {sketch_data['room_type']}. Here are the details:

    - Room dimensions: {sketch_data['dimensions']}
    - Layout notes: {sketch_data['layout_notes']}
    - Current furniture: {sketch_data['current_furniture']}
    - Desired furniture: {sketch_data['desired_furniture']}
    - Special considerations: {sketch_data['special_considerations']}
    - Style preference: {sketch_data['style']}
    - Budget: {sketch_data['budget']}

    Based on this, please provide:
    1. Layout tips or key placement advice
    2. Suggested furniture categories or types
    3. A follow-up message I can text or email the guest
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert interior designer and sales consultant for high-end furniture."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    return response.choices[0].message.content

def generate_note_from_prompt(prompt, client_data, sketch_data):
    name = client_data.get("name", "the client")
    room = sketch_data.get("room_type", "their space")
    style = client_data.get("style", "")
    layout = sketch_data.get("layout_notes", "")
    special = sketch_data.get("special_considerations", "")

    full_prompt = (
        f"Write a {prompt} for {name}. "
        f"Their room of interest is {room}. "
        f"They prefer a {style} style. "
        f"Layout notes: {layout}. "
        f"Special considerations: {special}."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": full_prompt}],
        max_tokens=400
    )

    return response.choices[0].message.content.strip()

def load_followup_templates():
    with open("templates/followups.json", "r") as f:
        return json.load(f)

def get_followup_template(guest_type, style):
    templates = load_followup_templates()
    return templates.get(guest_type, {}).get(style)

import streamlit as st
from openai import OpenAI

def generate_followup_from_template(client_type, message_style, client_data, sketch_data=None):
    sketch_data = sketch_data or {}

    template = FOLLOW_UP_MESSAGES.get(client_type, {}).get(message_style)
    if not template:
        return "⚠️ No message template available for this client type and style."

    template_text = (
        f"Subject: {template['subject']}\n\n{template['body']}" if isinstance(template, dict) else template
    )

    tone_instruction = FOLLOW_UP_TONES.get(message_style.lower(), "")

    prompt = f"""
You are a helpful, warm-toned furniture sales assistant writing a personalized {message_style} message.

Here is a sample template to use as a base:
\"\"\"{template_text}\"\"\"

Client Info:
Name: {client_data.get('name')}
Phone: {client_data.get('phone')}
Style Preference: {client_data.get('style')}
Rooms of Interest: {client_data.get('rooms')}
Budget: {client_data.get('budget')}

Room Sketch (latest):
Room: {sketch_data.get('room_type')}
Dimensions: {sketch_data.get('dimensions')}
Current Furniture: {sketch_data.get('current_furniture')}
Desired Furniture: {sketch_data.get('desired_furniture')}
Notes: {sketch_data.get('layout_notes')}

{tone_instruction}
Write this in a personal, human tone, avoiding robotic or generic phrasing.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for a furniture sales company."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.8
    )

    return response.choices[0].message.content.strip()


