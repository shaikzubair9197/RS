import google.generativeai as genai
import time
import re
from google.api_core.exceptions import ResourceExhausted
import json
from rapidfuzz import fuzz


# ✅ Your Gemini API Key
genai.configure(api_key="AIzaSyDJqoc-pfZpnh3nFGtIRcYCwSwFLKi0E7o")

def get_working_model():
    models = genai.list_models()
    for m in models:
        if "generateContent" in m.supported_generation_methods:
            print("✅ Using model:", m.name)
            return genai.GenerativeModel(m.name)
    raise Exception("❌ No working Gemini model found")

model = get_working_model()

# ✅ FALLBACK RULE-BASED CLASSIFIER (NO AI USED)

def fallback_classifier(text):
    text = text.lower()

    # ✅ Load patterns dynamically from JSON (NON-HARDCODED)
    with open("intent_config.json", "r") as f:
        patterns = json.load(f)

    best_match = None
    highest_score = 0

    for intent, phrases in patterns.items():
        for phrase in phrases:
            score = fuzz.partial_ratio(text, phrase.lower())

            if score > highest_score:
                highest_score = score
                best_match = intent

    # ✅ Confidence threshold
    if highest_score >= 70:
        return best_match

    return "NOT_INSURANCE_EMAIL"


def classify_email(subject, body):
    prompt_text = f"""
You are an insurance email classifier.

Classify into ONLY ONE category:

1. Policy Document Request
2. Claim Status
3. New Policy Inquiry
4. Payment Issue
5. Cancellation
6. Complaint

If not insurance related return:
NOT_INSURANCE_EMAIL

Subject: {subject}
Body: {body}

Return only category name.
"""

    try:
        # ✅ Slow down to avoid rate limit
        time.sleep(2)

        response = model.generate_content(prompt_text)
        return response.text.strip()

    except ResourceExhausted:
        print("⚠️ Gemini quota hit → Using fallback classifier")
        combined_text = f"{subject} {body}"
        return fallback_classifier(combined_text)

    except Exception as e:
        print("❌ AI Error:", str(e))
        combined_text = f"{subject} {body}"
        return fallback_classifier(combined_text)
