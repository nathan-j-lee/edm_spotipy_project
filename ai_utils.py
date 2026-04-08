from google import genai
from google.genai import types
import requests
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))

def extract_lineup_with_ai(url):
    prompt = f"""
    You are a professional music festival data extractor. 
    Your goal is to identify artist names from URLs given by the user.
    - Output ONLY a comma-separated list of names.
    - Exclude headers, dates, stage names, and 'special guest' labels.
    - Do not include any introductory text like 'Here are the artists'.
    - If no artists are found, return 'NONE'.
    - Treat B2B or / sets as separate artists and split them into individual names in the list. Do not duplicate artist names.
    """
    # We enable the 'url_context' tool so Gemini can visit the link
    config = types.GenerateContentConfig(
        tools=[types.Tool(url_context=types.UrlContext())],
        system_instruction=prompt
    )

    response = client.models.generate_content(
        model='gemini-3-flash-preview',
        contents=f"Please analyze this page and give me the lineup: {url}",
        config=config
    )

    return [name.strip() for name in response.text.split(',') if name.strip()]
    
