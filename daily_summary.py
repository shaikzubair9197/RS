import json
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

with open("output.json", "r") as f:
    data = json.load(f)

summary = {
    "date": today,
    "total_emails": len(data),
    "escalated_cases": 0,
    "intent_breakdown": {}
}

for record in data:
    intent = record["detected_intent"]

    summary["intent_breakdown"][intent] = summary["intent_breakdown"].get(intent, 0) + 1

    if record.get("escalated") is True:
        summary["escalated_cases"] += 1

with open(f"daily_summary_{today}.json", "w") as f:
    json.dump(summary, f, indent=4)

print("✅ Daily summary report generated")
