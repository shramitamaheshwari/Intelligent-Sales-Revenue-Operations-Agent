import requests
import os

HF_API_KEY = os.getenv("HF_API_KEY", "your_api_key_here")

def detect_competitor_intent(email_text: str):
    """
    Uses Hugging Face Zero-Shot NLI to detect competitor mentions.
    """
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    payload = {
        "inputs": email_text,
        "parameters": {
            "candidate_labels": [
                "pricing inquiry", 
                "competitor comparison", 
                "feature request", 
                "cancellation threat"
            ]
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def detect_passive_aggression(email_text: str):
    """
    Uses DistilBERT fine-tuned to detect passive-aggressive tone.
    """
    API_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": email_text}
    
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()
