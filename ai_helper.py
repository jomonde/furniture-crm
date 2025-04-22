import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
