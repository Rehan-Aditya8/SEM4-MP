import json
import os

MOCK_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'mock_emails.json')

class OutlookService:
    def __init__(self, use_mock=True):
        self.use_mock = use_mock

    def fetch_emails(self):
        if self.use_mock:
            return self._fetch_mock_emails()
        else:
            # Placeholder for real outlook integration
            return []

    def _fetch_mock_emails(self):
        try:
            with open(MOCK_DATA_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error fetching mock emails: {e}")
            return []
