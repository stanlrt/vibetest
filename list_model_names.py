import google.generativeai as genai
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Configure Google
if "GOOGLE_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Configure OpenAI
openai_client = None
if "OPENAI_API_KEY" in os.environ:
    openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

with open("model_names.txt", "w") as f:
    # List Google Models
    if "GOOGLE_API_KEY" in os.environ:
        try:
            for model in genai.list_models():
                if "generateContent" in model.supported_generation_methods:
                    f.write(f"{model.name}\n")
        except Exception as e:
            print(f"Error listing Google models: {e}")

    # List OpenAI Models
    if openai_client:
        try:
            models = openai_client.models.list()
            for model in models:
                f.write(f"{model.id}\n")
        except Exception as e:
            print(f"Error listing OpenAI models: {e}")
