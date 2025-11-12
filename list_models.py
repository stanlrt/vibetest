import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv() # Load from .env file

# Configure the API key
if "GOOGLE_API_KEY" not in os.environ:
    print("GOOGLE_API_KEY environment variable not set.")
    exit()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(f"Name: {model.name}")
        print(f"  Description: {model.description}")
        print(f"  Supported methods: {model.supported_generation_methods}\n")
