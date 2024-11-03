from django.conf import settings
import logging, requests, base64
from typing import List, Dict

logger = logging.getLogger(__name__)

class CodeExecutionService:
    """Separate client class to handle Judge0 API interactions"""
    BASE_URL = "https://judge0-ce.p.rapidapi.com"

    def __init__(self):
        self.headers = {
            "x-rapidapi-key": settings.RAPIDAPI_KEY,
            "x-rapidapi-host": "judge0-ce.p.rapidapi.com",
            "Content-Type": "application/json"
        }

    def submit_code(self, source_code: str, test_cases: List[Dict[str, any]]) -> dict:
        """Perform batch submission to Judge0"""
        try:
            url = f"{self.BASE_URL}/submissions/batch?base64_encoded=true"
            payload = {
                "submissions": [
                    {
                        "source_code": base64.b64encode(source_code.encode()).decode(),
                        "language_id": 100,
                        "stdin": base64.b64encode(tc["input"].encode()).decode(),
                        "expected_output": base64.b64encode(tc["output"].encode()).decode()
                    }
                    for tc in test_cases
                ]
            }

            response = requests.post(url, headers=self.headers, json=payload)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error submitting code to Judge0: {str(e)}")
            raise

    def get_submission_result(self, tokens: List[Dict[str, str]]) -> dict:
        """Get batch submission result from judge0"""
        try:
            querystring = {"tokens": ",".join([t["token"] for t in tokens])}
            url = f"{self.BASE_URL}/submissions/batch"
            response = requests.get(url, headers=self.headers, params=querystring)
            return response.json()            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting submission result: {str(e)}")
            raise
