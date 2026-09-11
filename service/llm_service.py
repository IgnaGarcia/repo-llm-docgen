import logging
import time

from google import genai
from google.genai import types

RETRYABLE_STATUS_CODES = (429, 500, 502, 503, 504)
MAX_RETRIES = 3
BASE_DELAY_SECONDS = 2


class LlmService:
    def __init__(
        self,
        api_key,
        model_name="gemini-2.5-flash",
        thinking_level=None,
        max_retries=MAX_RETRIES,
    ):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.thinking_level = thinking_level or "MEDIUM"
        self.max_retries = max_retries

    def process_request(self, prompt, response_format="application/json"):
        messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]
        config = types.GenerateContentConfig(
            response_mime_type=response_format,
            temperature=0.1,
        )
        if self.thinking_level:
            config.thinking_config = types.ThinkingConfig(
                thinking_level=types.ThinkingLevel(self.thinking_level.upper())
            )

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=messages,
                    config=config,
                )

                usage = response.usage_metadata
                if usage:
                    logging.info(
                        f"[{self.model_name}] tokens - prompt: {usage.prompt_token_count}, "
                        f"output: {usage.candidates_token_count}, total: {usage.total_token_count}"
                    )

                return response.text

            except Exception as e:
                if attempt == self.max_retries or not self._is_retryable(e):
                    raise
                delay = BASE_DELAY_SECONDS * (2 ** (attempt - 1))
                logging.warning(
                    f"[{self.model_name}] Transient error on attempt {attempt}/{self.max_retries}: {e}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)

    def _is_retryable(self, error):
        code = getattr(error, "code", None)
        if code in RETRYABLE_STATUS_CODES:
            return True
        message = str(error)
        return "UNAVAILABLE" in message or any(
            str(status) in message for status in RETRYABLE_STATUS_CODES
        )
