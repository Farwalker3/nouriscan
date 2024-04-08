### Food Calories calculator APP
from dotenv import load_dotenv

load_dotenv() ## load all the environment variables

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Function to load Google Gemini Pro Vision API And get response

def get_gemini_repsonse(input, image, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, image[0], prompt])
    return response.text

def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

##initialize our streamlit app

st.set_page_config(page_title="NouriScan", page_icon="🍏")

st.header("NouriScan")
input_text = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image = ""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

submit = st.button("Tell me the nutritional information")

input_prompt = """
You are an expert nutritionist tasked with analyzing food items from the image to calculate their nutritional information. Please provide the following details for each food item:

| # | Food Item        | Quantity          | Calories | Carbohydrates (g) | Protein (g) | Fat (g) | Fiber (g) | Sodium (mg) |
|---|------------------|-------------------|----------|--------------------|-------------|---------|-----------|-------------|
| 1 | [Food Item 1]    | [Quantity 1]      | [Cal 1]  | [Carb 1]           | [Protein 1] | [Fat 1] | [Fiber 1] | [Sodium 1]  |
| 2 | [Food Item 2]    | [Quantity 2]      | [Cal 2]  | [Carb 2]           | [Protein 2] | [Fat 2] | [Fiber 2] | [Sodium 2]  |
|   |                  |                   |          |                    |             |         |           |             |

"""

response_header = """
## Nutritional Information for Food Items
"""

def format_response(food_items):
    response = response_header
    response += "| # | Food Item        | Quantity          | Calories | Carbohydrates (g) | Protein (g) | Fat (g) | Fiber (g) | Sodium (mg) |\n"
    response += "|---|------------------|-------------------|----------|--------------------|-------------|---------|-----------|-------------|\n"

    for idx, item in enumerate(food_items, 1):
        response += f"| {idx} | {item['Name']} | {item['Quantity']} | {item['Calories']} | {item['Carbohydrates']} | {item['Protein']} | {item['Fat']} | {item['Fiber']} | {item['Sodium']} |\n"

    total_calories = sum(item['Calories'] for item in food_items)
    total_carbs = sum(item['Carbohydrates'] for item in food_items)
    total_protein = sum(item['Protein'] for item in food_items)
    total_fat = sum(item['Fat'] for item in food_items)
    total_fiber = sum(item['Fiber'] for item in food_items)
    total_sodium = sum(item['Sodium'] for item in food_items)

    # Add totals row
    response += f"| **Total** | | | **{total_calories}** | **{total_carbs}** | **{total_protein}** | **{total_fat}** | **{total_fiber}** | **{total_sodium}** |\n"

    return response

## If submit button is clicked

if submit:
    image_data = input_image_setup(uploaded_file)
    response_text = get_gemini_repsonse(input_text, image_data, input_prompt)
    food_items = []
    response_lines = response_text.split('\n')
    for line in response