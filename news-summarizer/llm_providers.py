import openai
import cohere
from config import OPENAI_API_KEY, COHERE_API_KEY

# Initialize the OpenAI client only when an API key is available.
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Initialize the Cohere client (Fallback) only when an API key is available.
cohere_client = cohere.ClientV2(api_key=COHERE_API_KEY) if COHERE_API_KEY else None

def ask_openai(prompt):
    """Sends a prompt to OpenAI's GPT-4o-mini model."""
    if not openai_client:
        print("OpenAI API key is missing. Add OPENAI_API_KEY to the .env file.")
        return None

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI failed: {e}")
        return None


def ask_cohere(prompt):
    """Sends a prompt to Cohere's Command model."""
    if not cohere_client:
        print("Cohere API key is missing. Add COHERE_API_KEY to the .env file.")
        return None

    try:
        response = cohere_client.chat(
            model="command-r-plus-08-2024",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.text.strip()
    except Exception as e:
        print(f"Cohere failed: {e}")
        return None

