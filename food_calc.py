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
      # Prompt the user to allow camera and video autoplay permissions using JavaScript
      permission_script = """
      <script>
        async function askForPermissions() {
          try {
            await navigator.mediaDevices.getUserMedia({ video: true });
            console.log("Camera permissions granted");
          } catch (error) {
            console.error("Error accessing camera:", error);
          }
        }
        
        async function tryAutoplay() {
          const videoElement = document.createElement('video');
          videoElement.setAttribute('playsinline', '');
          videoElement.setAttribute('autoplay', '');
          videoElement.setAttribute('muted', '');
          videoElement.setAttribute('loop', '');
      
          try {
            await videoElement.play();
            console.log("Video autoplay permissions granted");
          } catch (error) {
            console.error("Error autoplaying video:", error);
            // Directly inform the user to allow autoplay
            const autoplayInfo = document.createElement('p');
            autoplayInfo.textContent = 'To use the camera, please allow autoplay by clicking on this message.';
            autoplayInfo.style.cursor = 'pointer';
            autoplayInfo.onclick = async () => {
              try {
                await videoElement.play();
                autoplayInfo.style.display = 'none'; // Hide the message after autoplay is allowed
                console.log("Video autoplay permissions granted after click");
              } catch (error) {
                console.error("Error autoplaying video after click:", error);
              }
            };
            document.body.appendChild(autoplayInfo);
          }
        }
      
        askForPermissions();
        tryAutoplay();
      </script>
      """
    
      # Display the prompt to the user
      st.write(permission_script, unsafe_allow_html=True)
    
      # Now you can use st.camera_input() to capture images
      camera_image = st.camera_input("Take a picture")
    
      if camera_image is not None:
          st.image(camera_image, caption="Captured Image", use_column_width=True)

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
                    "CA": "Calcium",
                    "CHOCDF": "Carbohydrates",
                    "CHOCDF.net": "Net Carbs",
                    "CHOLE": "Cholesterol",
                    "ENERC_KCAL": "Calories",
                    "FAMS": "Monounsaturated Fat",
                    "FAPU": "Polyunsaturated Fat",
                    "FASAT": "Saturated Fat",
                    "FAT": "Total Fat",
                    "FATRN": "Trans Fat",
                    "FE": "Iron",
                    "FIBTG": "Dietary Fiber",
                    "FOLAC": "Folate",
                    "FOLDFE": "Folate (DFE)",
                    "FOLFD": "Folate (food)",
                    "K": "Potassium",
                    "MG": "Magnesium",
                    "NA": "Sodium",
                    "NIA": "Niacin (B3)",
                    "P": "Phosphorus",
                    "PROCNT": "Protein",
                    "RIBF": "Riboflavin (B2)",
                    "SUGAR": "Sugar",
                    "SUGAR.added": "Added Sugar",
                    "THIA": "Thiamin (B1)",
                    "TOCPHA": "Vitamin E",
                    "VITA_RAE": "Vitamin A",
                    "VITB12": "Vitamin B12",
                    "VITB6A": "Vitamin B6",
                    "VITC": "Vitamin C",
                    "VITD": "Vitamin D",
                    "VITK1": "Vitamin K",
                    "WATER": "Water",
                    "ZN": "Zinc"
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
                "CA": "Calcium",
                "CHOCDF": "Carbohydrates",
                "CHOCDF.net": "Net Carbs",
                "CHOLE": "Cholesterol",
                "ENERC_KCAL": "Calories",
                "FAMS": "Monounsaturated Fat",
                "FAPU": "Polyunsaturated Fat",
                "FASAT": "Saturated Fat",
                "FAT": "Total Fat",
                "FATRN": "Trans Fat",
                "FE": "Iron",
                "FIBTG": "Dietary Fiber",
                "FOLAC": "Folate",
                "FOLDFE": "Folate (DFE)",
                "FOLFD": "Folate (food)",
                "K": "Potassium",
                "MG": "Magnesium",
                "NA": "Sodium",
                "NIA": "Niacin (B3)",
                "P": "Phosphorus",
                "PROCNT": "Protein",
                "RIBF": "Riboflavin (B2)",
                "SUGAR": "Sugar",
                "SUGAR.added": "Added Sugar",
                "THIA": "Thiamin (B1)",
                "TOCPHA": "Vitamin E",
                "VITA_RAE": "Vitamin A",
                "VITB12": "Vitamin B12",
                "VITB6A": "Vitamin B6",
                "VITC": "Vitamin C",
                "VITD": "Vitamin D",
                "VITK1": "Vitamin K",
                "WATER": "Water",
                "ZN": "Zinc"
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