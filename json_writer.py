import json
from datetime import datetime
import hashlib

def generate_hash(sender, subject, body):
    raw = f"{sender}|{subject}|{body}"
    return hashlib.md5(raw.encode()).hexdigest()

def save_to_json(email_data):
    try:
        with open("output.json", "r") as f:
            data = json.load(f)
    except:
        data = []

    email_hash = generate_hash(
        email_data["from"],
        email_data["subject"],
        email_data["body"]
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for record in data:
        if record["email_hash"] == email_hash:
            record["repeat_count"] += 1
            record["last_seen"] = now

            # ✅ AUTO ESCALATION LOGIC
            if record["repeat_count"] >= 3:
                record["escalated"] = True

            with open("output.json", "w") as f:
                json.dump(data, f, indent=4)

            print("🔁 Duplicate detected → Count Updated → Escalation Checked")
            return

    email_data["email_hash"] = email_hash
    email_data["first_seen"] = now
    email_data["last_seen"] = now
    email_data["repeat_count"] = 1
    email_data["escalated"] = False

    data.append(email_data)

    with open("output.json", "w") as f:
        json.dump(data, f, indent=4)

    print("✅ New unique email saved")
