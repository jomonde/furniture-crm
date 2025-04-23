from openai import OpenAI
import os
import json
import streamlit as st

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

def generate_followup_from_template(template_text, client_data, sketch_data=None, message_style="text"):
    sketch_data = sketch_data or {}

    # Add tone guidance based on style
    style_instructions = {
        "text": "Keep it short, casual, and friendly—like you're texting someone you’ve already spoken to.",
        "phone": "Write it like a quick phone call script—natural and spoken, with a warm greeting and easy closing.",
        "email": "Make it slightly longer and thoughtful. Include a warm intro, body with value, and a polite call-to-action.",
        "handwritten": "Be heartfelt, personal, and brief—as if writing a quick thank-you note."
    }

    tone_instruction = style_instructions.get(message_style.lower(), "")

    prompt = f"""You are a helpful, warm-toned furniture sales assistant writing a personalized follow-up message.

Here is a sample template to base your message on:
"{template_text}"

Client Info:
Name: {client_data.get('name')}
Phone: {client_data.get('phone')}
Style: {client_data.get('style')}
Rooms of Interest: {client_data.get('rooms')}
Budget: {client_data.get('budget')}

Room Sketch (latest):
Room: {sketch_data.get('room_type')}
Dimensions: {sketch_data.get('dimensions')}
Current Furniture: {sketch_data.get('current_furniture')}
Desired Furniture: {sketch_data.get('desired_furniture')}
Notes: {sketch_data.get('layout_notes')}

{tone_instruction}
"""

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful and friendly assistant who writes follow-up messages for a furniture store."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.8
    )

    return response.choices[0].message.content.strip()


