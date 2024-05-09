import requests
from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from decimal import Decimal

# Load environment variables
load_dotenv()

# Configure genAI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to retrieve nutrition information for a food item
def get_nutrition_info(food_item):
    url = 'https://api.edamam.com/api/nutrition-data'
    app_id = os.getenv("EDAMAM_APP_ID")
    app_key = os.getenv("EDAMAM_APP_KEY")
    params = {
        'app_id': app_id,
        'app_key': app_key,
        'nutrition-type': 'logging',
        'ingr': food_item
    }
    response = requests.get(url, params=params)
    return response.json()

# Function to load Google Gemini Pro Vision API And get response
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to prepare image data for genAI API
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
st.set_page_config(page_title="Intelligent Food Calories Calculator",layout="wide")

st.header("Intelligent Food Calories Calculator")
col1, col2 = st.columns([1, 3])
with col1:
  # Add Additional Commands Drawer
  add_commands_expander = st.expander("Add Additional Commands (Optional)")

  with add_commands_expander:
      st.subheader("Input Prompt:")
      input_prompt = """
      You are an expert in nutritionist where you need to list the food items/ingredients from the image in the below format:

      [amount/quantity] Item 1, [amount/quantity] Item 2, ----, ----
      """

      input_text = st.text_input("Input Prompt: ", key="input")

  uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
  camera_option = st.checkbox("Use Camera")

  if camera_option:
      camera_image = st.camera_input("Take a picture")

      if camera_image is not None:
          submit_button = st.button("Analyze Picture")

          if submit_button:
              image_data = input_image_setup(camera_image)

              # Get response from genAI API
              response = get_gemini_response(input_text, image_data, input_prompt)
              detected_food_items = response.split(',')
              with col2:
                st.subheader("Detected Food Items:")
                st.write(detected_food_items)

                st.subheader("Nutrition Information:")

                # Create a dictionary to hold the nutrition information for each food item
                nutrition_data = {}

                for food_item in detected_food_items:
                    # Get nutrition information for each food item
                    nutrition_info = get_nutrition_info(food_item)
                    # Store the nutrition information in the dictionary
                    nutrition_data[food_item] = nutrition_info['totalNutrients']

                # Create a table for the nutrition information
                table_data = []
                nutrients = set()
                for food_item, info in nutrition_data.items():
                    for nutrient, data in info.items():
                        nutrients.add(nutrient)
                nutrients = sorted(list(nutrients))

                # Create a header row
                header_row = ["Nutrient"]
                header_row.extend(detected_food_items)
                table_data.append(header_row)

                # Mapping of nutrient acronyms to their full names
                nutrient_mapping = {
                    "CA": "Calcium (mg)",
                    "CHOCDF": "Carbohydrates (g)",
                    "CHOCDF.net": "Net Carbs (g)",
                    "CHOLE": "Cholesterol (mg)",
                    "ENERC_KCAL": "Calories (kcal)",
                    "FAMS": "Monounsaturated Fat (g)",
                    "FAPU": "Polyunsaturated Fat (g)",
                    "FASAT": "Saturated Fat (g)",
                    "FAT": "Total Fat (g)",
                    "FATRN": "Trans Fat (g)",
                    "FE": "Iron (mg)",
                    "FIBTG": "Dietary Fiber (g)",
                    "FOLAC": "Folate (µg)",
                    "FOLDFE": "Folate (DFE) (µg)",
                    "FOLFD": "Folate (food) (µg)",
                    "K": "Potassium (mg)",
                    "MG": "Magnesium (mg)",
                    "NA": "Sodium (mg)",
                    "NIA": "Niacin (B3) (mg)",
                    "P": "Phosphorus (mg)",
                    "PROCNT": "Protein (g)",
                    "RIBF": "Riboflavin (B2) (mg)",
                    "SUGAR": "Sugar (g)",
                    "SUGAR.added": "Added Sugar (g)",
                    "THIA": "Thiamin (B1) (mg)",
                    "TOCPHA": "Vitamin E (mg)",
                    "VITA_RAE": "Vitamin A (µg)",
                    "VITB12": "Vitamin B12 (µg)",
                    "VITB6A": "Vitamin B6 (mg)",
                    "VITC": "Vitamin C (mg)",
                    "VITD": "Vitamin D (µg)",
                    "VITK1": "Vitamin K (µg)",
                    "WATER": "Water (g)",
                    "ZN": "Zinc (mg)"
                }

                # Populate the table data
                for nutrient in nutrients:
                    row = [nutrient_mapping.get(nutrient, nutrient)]
                    for food_item in detected_food_items:
                        if nutrient in nutrition_data.get(food_item, {}):
                          quantity = nutrition_data[food_item][nutrient]["quantity"]
                          rounded_quantity = round(float(quantity))
                          row.append(Decimal(rounded_quantity))
                        else:
                            row.append("N/A")
                    table_data.append(row)

                # Display the table
                st.table(table_data)

  if uploaded_file is not None and not camera_option:
      image = Image.open(uploaded_file)
      st.image(image, caption="Uploaded Image.", use_column_width=True)

      submit_button = st.button("Tell me the total calories")

      if submit_button:
          image_data = input_image_setup(uploaded_file)

          # Get response from genAI API
          response = get_gemini_response(input_text, image_data, input_prompt)
          detected_food_items = response.split(',')
          with col2:
            st.subheader("Detected Food Items:")
            st.write(detected_food_items)

            st.subheader("Nutrition Information:")

            # Create a dictionary to hold the nutrition information for each food item
            nutrition_data = {}

            for food_item in detected_food_items:
                # Get nutrition information for each food item
                nutrition_info = get_nutrition_info(food_item)
                # Store the nutrition information in the dictionary
                nutrition_data[food_item] = nutrition_info['totalNutrients']

            # Create a table for the nutrition information
            table_data = []
            nutrients = set()
            for food_item, info in nutrition_data.items():
                for nutrient, data in info.items():
                    nutrients.add(nutrient)
            nutrients = sorted(list(nutrients))

            # Create a header row
            header_row = ["Nutrient"]
            header_row.extend(detected_food_items)
            table_data.append(header_row)

            # Mapping of nutrient acronyms to their full names
            nutrient_mapping = {
                "CA": "Calcium (mg)",
                "CHOCDF": "Carbohydrates (g)",
                "CHOCDF.net": "Net Carbs (g)",
                "CHOLE": "Cholesterol (mg)",
                "ENERC_KCAL": "Calories (kcal)",
                "FAMS": "Monounsaturated Fat (g)",
                "FAPU": "Polyunsaturated Fat (g)",
                "FASAT": "Saturated Fat (g)",
                "FAT": "Total Fat (g)",
                "FATRN": "Trans Fat (g)",
                "FE": "Iron (mg)",
                "FIBTG": "Dietary Fiber (g)",
                "FOLAC": "Folate (µg)",
                "FOLDFE": "Folate (DFE) (µg)",
                "FOLFD": "Folate (food) (µg)",
                "K": "Potassium (mg)",
                "MG": "Magnesium (mg)",
                "NA": "Sodium (mg)",
                "NIA": "Niacin (B3) (mg)",
                "P": "Phosphorus (mg)",
                "PROCNT": "Protein (g)",
                "RIBF": "Riboflavin (B2) (mg)",
                "SUGAR": "Sugar (g)",
                "SUGAR.added": "Added Sugar (g)",
                "THIA": "Thiamin (B1) (mg)",
                "TOCPHA": "Vitamin E (mg)",
                "VITA_RAE": "Vitamin A (µg)",
                "VITB12": "Vitamin B12 (µg)",
                "VITB6A": "Vitamin B6 (mg)",
                "VITC": "Vitamin C (mg)",
                "VITD": "Vitamin D (µg)",
                "VITK1": "Vitamin K (µg)",
                "WATER": "Water (g)",
                "ZN": "Zinc (mg)"
            }

            # Populate the table data
            for nutrient in nutrients:
                row = [nutrient_mapping.get(nutrient, nutrient)]
                for food_item in detected_food_items:
                    if nutrient in nutrition_data.get(food_item, {}):
                      quantity = nutrition_data[food_item][nutrient]["quantity"]
                      rounded_quantity = round(float(quantity))
                      row.append(Decimal(rounded_quantity))
                    else:
                        row.append("N/A")
                table_data.append(row)

            # Display the table
            st.table(table_data)