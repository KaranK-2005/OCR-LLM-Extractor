import json


class ReceiptParser:
    """Parser for the LLM's response."""

    def parse(self, response: str) -> dict:
        """Parse the LLM's response and return a JSON object."""
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:-4]
            elif response.startswith("```"):
                response = response[3:-3]
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "The LLM's response was not valid JSON."}
