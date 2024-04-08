### Food Calories calculator APP
from dotenv import load_dotenv

load_dotenv() ## load all the environment variables

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Function to load Google Gemini Pro Vision API And get response

def get_gemini_repsonse(input,image,prompt):
    model=genai.GenerativeModel('gemini-pro-vision')
    response=model.generate_content([input,image[0],prompt])
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

st.set_page_config(page_title="Intelligent Food Calories Calculator")

st.header("Intelligent Food Calories Calculator")
input=st.text_input("Input Prompt: ",key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image=""   
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)


submit=st.button("Tell me the total calories")

input_prompt="""
You are an expert nutritionist tasked with analyzing food items from the image to calculate their nutritional information. Please provide the following details for each food item:

1. Name of the food item
2. Quantity or portion size
3. Calories
4. Carbohydrates (in grams)
5. Protein (in grams)
6. Fat (in grams)
7. Fiber (in grams)
8. Sodium (in milligrams)
9. Any other relevant nutritional information

Example:
- Item 1:
    - Name: Apple
    - Quantity: 1 medium
    - Calories: 95
    - Carbohydrates: 25
    - Protein: 0.5
    - Fat: 0.3
    - Fiber: 4.4
    - Sodium: 0
    - Other: Rich in vitamin C

- Item 2:
    - Name: Chicken Breast
    - Quantity: 100 grams
    - Calories: 165
    - Carbohydrates: 0
    - Protein: 31
    - Fat: 3.6
    - Fiber: 0
    - Sodium: 74
    - Other: High in protein, low in fat
"""

## If submit button is clicked

if submit:
    image_data=input_image_setup(uploaded_file)
    response=get_gemini_repsonse(input_prompt,image_data,input)
    st.subheader("The Response is")
    st.write(response)