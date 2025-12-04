from gmail_reader import read_all_unread_allowed_emails
from classifier import classify_email
from json_writer import save_to_json

print("✅ Checking UNREAD allowed sender emails...")

emails = read_all_unread_allowed_emails(limit=50)

if not emails:
    print("❌ No unread allowed sender emails found.")
    exit()

print(f"✅ Found {len(emails)} new unread allowed emails\n")

for idx, email in enumerate(emails, start=1):
    sender = email["from"]
    subject = email["subject"]
    body = email["body"]

    print(f"📨 Processing Email #{idx}")
    print("From:", sender)
    print("Subject:", subject)

    # ✅ Safe AI classification (with fallback inside classifier.py)
    intent = classify_email(subject, body)
    print("✅ Detected Intent:", intent)

    # ✅ Tag whether it came from AI or fallback
    ai_status = "AI_USED" if intent != "NOT_INSURANCE_EMAIL" else "FALLBACK_USED"

    email_data = {
        "from": sender,
        "subject": subject,
        "body": body,
        "detected_intent": intent,
        "ai_status": ai_status
    }

    save_to_json(email_data)
    print("-" * 50)

print("✅ All unread emails processed successfully")
