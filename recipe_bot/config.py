import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
BRAINTRUST_API_KEY = os.getenv("BRAINTRUST_API_KEY")

MODEL_NAME = "gpt-4o-mini"
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# System prompt for recipe generation
RECIPE_SYSTEM_PROMPT = "You are a helpful cooking assistant who creates safe, delicious recipes. Always carefully consider any dietary requirements, allergies, or restrictions provided by the user. Generate recipes in valid JSON format and ensure all ingredients and suggestions are safe for the user's dietary needs."