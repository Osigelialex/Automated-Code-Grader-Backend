from django.conf import settings
import logging, requests
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
            # not using base64 encoding for now because of unhashable data types
            url = f"{self.BASE_URL}/submissions/batch?base64_encoded=false"
            payload = {
                "submissions": [
                    {
                        "source_code": source_code,
                        "language_id": 100,
                        "stdin": tc["input"],
                        "expected_output": tc["output"]
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
