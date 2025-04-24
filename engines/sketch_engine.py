# sketch_engine.py

from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_sketch_summary(sketch_data, client_data=None):
    prompt = f"""
You are a professional interior designer helping a furniture consultant understand a room's layout and potential based on client input.

Room Type: {sketch_data.get('room_type')}
Dimensions: {sketch_data.get('dimensions')}
Layout Notes: {sketch_data.get('layout_notes')}
Current Furniture: {sketch_data.get('current_furniture')}
Desired Furniture: {sketch_data.get('desired_furniture')}
Special Considerations: {sketch_data.get('special_considerations')}

{"Client Style Preference: " + client_data.get('style') if client_data else ""}

Please summarize the key characteristics of this room, and provide helpful design suggestions, such as:
- How to optimize layout
- Style or space planning tips
- Any hidden opportunities for other furniture or accessories

Keep the tone collaborative, brief, and helpful for a sales/design discussion.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a skilled furniture layout and style advisor."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()
