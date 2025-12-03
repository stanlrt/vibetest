import abc
import os
import re
import json
import google.generativeai as genai
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


def fix_json_trailing_commas(json_str: str) -> str:
    """
    Remove trailing commas before closing brackets/braces in JSON.
    LLMs sometimes produce invalid JSON with trailing commas like {"key": "value",}
    """
    # Remove trailing commas before } or ]
    # This regex finds comma followed by optional whitespace and then } or ]
    pattern = r',(\s*[}\]])'
    return re.sub(pattern, r'\1', json_str)


class LLMProvider(abc.ABC):
    @abc.abstractmethod
    async def generate_json(self, prompt: str, system_instruction: str, model_name: str) -> dict:
        pass


class GoogleProvider(LLMProvider):
    def __init__(self):
        if "GOOGLE_API_KEY" not in os.environ:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

    async def generate_json(self, prompt: str, system_instruction: str, model_name: str) -> dict:
        model = genai.GenerativeModel(model_name)
        full_prompt = f"{system_instruction}\n\n{prompt}"
        response = await model.generate_content_async(full_prompt)

        response_text = response.text
        # Clean issues with responses wrapped in code blocks
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()

        # Fix trailing commas that LLMs sometimes produce
        response_text = fix_json_trailing_commas(response_text)

        return json.loads(response_text)


class OpenAIProvider(LLMProvider):
    def __init__(self):
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        self.client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

    async def generate_json(self, prompt: str, system_instruction: str, model_name: str) -> dict:
        response = await self.client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        response_text = response.choices[0].message.content or ""
        return json.loads(response_text)


def get_provider(model_name: str) -> LLMProvider:
    # Google models usually start with "models/" or contain "gemini" / "gemma"
    if model_name.startswith("models/") or "gemini" in model_name or "gemma" in model_name:
        return GoogleProvider()

    # OpenAI models
    openai_prefixes = [
        "gpt", "chatgpt", "o1", "o3", "o4"
    ]

    if any(model_name.startswith(prefix) for prefix in openai_prefixes):
        return OpenAIProvider()

    else:
        # Default fallback or error? Let's try to infer or default to OpenAI if it looks like a GPT model, otherwise error.
        # For now, let's be strict to avoid confusion.
        raise ValueError(
            f"Unknown model provider for model: {model_name}. Please use a known prefix (models/ for Google, gpt- for OpenAI).")
