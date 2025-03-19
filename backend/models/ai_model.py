import requests
import os

class AIModel:
    def __init__(self):
        self.api_url = 'https://api-inference.huggingface.co/models/facebook/bart-large-cnn'
        # Use HF_TOKEN from environment, no hardcoded default
        self.api_key = os.getenv('HF_TOKEN')  # Line 7 now safe

        # Optional: Raise an error if HF_TOKEN is missing
        if not self.api_key:
            raise ValueError("HF_TOKEN environment variable not set. Please set it to your Hugging Face API key.")

    def summarize(self, logs):
        text = ' '.join([f"{log['timestamp']} {log['level']} {log['message']}" for log in logs])
        if not text.strip():
            return {'summary': 'No content to summarize'}
        headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}
        payload = {'inputs': text[:1000], 'parameters': {'max_length': 100, 'min_length': 30}}
        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            if response.status_code == 200:
                raw_summary = response.json()[0]['summary_text']
                print(f"Raw API summary: {raw_summary}")
                cleaned_summary = raw_summary.replace("Back to the page you came from.", "").strip()
                return {'summary': cleaned_summary}
            return {'summary': f'Error: Could not summarize (Status: {response.status_code})'}
        except Exception as e:
            return {'summary': f'Error: Summarization failed - {str(e)}'}