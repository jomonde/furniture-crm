# message_engine.py

from templates.followups import FOLLOW_UP_MESSAGES
from templates.followup_tones import FOLLOW_UP_TONES
from ai_helper import client  # OpenAI client already initialized in ai_helper.py

def get_template_text(client_type, style):
    template = FOLLOW_UP_MESSAGES.get(client_type, {}).get(style)
    if not template:
        return None

    if isinstance(template, dict):
        return f"Subject: {template['subject']}\n\n{template['body']}"
    return template


def get_tone_instruction(style):
    return FOLLOW_UP_TONES.get(style.lower(), "")


def generate_message_prompt(template_text, client_data, sketch_data=None, tone_instruction=""):
    sketch_data = sketch_data or {}

    prompt = f"""
You are a helpful, warm-toned furniture sales assistant writing a personalized {client_data.get('style', 'text')} follow-up message.

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
Write this in a personal, natural voice. Avoid robotic language. Be helpful and human.
"""
    return prompt


def generate_followup_message(client_type, style, client_data, sketch_data=None):
    template_text = get_template_text(client_type, style)
    tone_instruction = get_tone_instruction(style)

    if not template_text:
        return "⚠️ No message template found for this type/style."

    prompt = generate_message_prompt(template_text, client_data, sketch_data, tone_instruction)

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
