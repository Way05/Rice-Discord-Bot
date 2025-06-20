from dotenv import load_dotenv
import os
from google import genai

load_dotenv()
token = os.getenv("GEMINI_TOKEN")

client = genai.Client(api_key=token)

def getResponse(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    
    return response.text