from google import genai
from google.genai import types


class LlmService:
    def __init__(self, api_key, model_name="gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def process_request(self, prompt, response_format="application/json"):
        messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]
        config = types.GenerateContentConfig(
            response_mime_type=response_format,
            temperature=0.1,
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=messages,
            config=config,
        )

        return response.text
