import time
import openai
from abc import ABC

class OpenAIEngine(ABC):
    def __init__(self):
        self._client = openai.OpenAI(
            base_url="",
            api_key="" # YOUR-API-KEY
        )

    # Load environment variables from .env file
    def get_LLM_response(self, **kwargs):
        for _ in range(10):
            try:
                response = self._client.chat.completions.create(**kwargs)
                return response.model_dump()  # If the above succeeds, we return here
            except Exception as e:
                save_err = e
                if isinstance(e, openai.error.ServiceUnavailableError):
                    time.sleep(1)
                elif "The server had an error processing your request." in str(e):
                    time.sleep(1)
                else:
                    break
        raise save_err