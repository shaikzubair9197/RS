import os
import pickle
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']  # ✅ MODIFY to mark as read

ALLOWED_SENDERS = [
    "nikkypradhan93913@gmail.com",
    "jimelliotivanp@gmail.com"
]

def get_gmail_service():
    creds = None

    if os.path.exists("token.json"):
        with open("token.json", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)

        with open("token.json", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


def read_all_unread_allowed_emails(limit=20):
    service = get_gmail_service()

    results = service.users().messages().list(
        userId='me',
        q="is:unread",   # ✅ ONLY UNREAD EMAILS
        maxResults=limit
    ).execute()

    messages = results.get('messages', [])
    allowed_emails = []

    for msg in messages:
        msg_id = msg['id']
        message = service.users().messages().get(
            userId='me', id=msg_id
        ).execute()

        headers = message['payload']['headers']
        subject = ""
        sender = ""

        for h in headers:
            if h['name'] == "Subject":
                subject = h['value']
            if h['name'] == "From":
                sender = h['value']

        if any(allowed.lower() in sender.lower() for allowed in ALLOWED_SENDERS):

            body = ""
            if 'parts' in message['payload']:
                part = message['payload']['parts'][0]
                body = base64.urlsafe_b64decode(
                    part['body']['data']
                ).decode("utf-8", errors="ignore")
            else:
                body = base64.urlsafe_b64decode(
                    message['payload']['body']['data']
                ).decode("utf-8", errors="ignore")

            allowed_emails.append({
                "from": sender,
                "subject": subject,
                "body": body,
                "msg_id": msg_id
            })

            # ✅ MARK EMAIL AS READ
            service.users().messages().modify(
                userId="me",
                id=msg_id,
                body={"removeLabelIds": ["UNREAD"]}
            ).execute()

    return allowed_emails
