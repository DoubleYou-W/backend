import os
import base64
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from email import message_from_bytes
from email.header import decode_header

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_URL_UPDATE = f"{API_URL}/api/update"

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

TOKEN_PATH = './services/token.json'
CREDENTIALS_PATH = './services/credentials.json'

def authenticate():
    creds = None
    
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
    
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def decode_mime_header(header_value):
    decoded_fragments = decode_header(header_value)
    decoded = ''

    for fragment, encoding in decoded_fragments:
        if isinstance(fragment, bytes):
            decoded += fragment.decode(encoding or 'utf-8', errors='ignore')
        else:
            decoded += fragment

    return decoded

def extract_email_body(email_msg):
    plain_text = None
    html_text = None

    if email_msg.is_multipart():
        for part in email_msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", "")).lower()

            if "attachment" in content_disposition:
                continue

            try:
                payload = part.get_payload(decode=True)
                text = payload.decode(part.get_content_charset('utf-8'), errors='ignore').strip()
            except Exception:
                continue

            if content_type == "text/plain" and not plain_text:
                plain_text = text
            elif content_type == "text/html" and not html_text:
                html_text = text
    else:
        content_type = email_msg.get_content_type()

        try:
            payload = email_msg.get_payload(decode=True)
            text = payload.decode(email_msg.get_content_charset('utf-8'), errors='ignore').strip()
        except Exception:
            text = ""

        if content_type == "text/plain":
            plain_text = text
        elif content_type == "text/html":
            html_text = text

    if plain_text:
        return plain_text
    elif html_text:
        soup = BeautifulSoup(html_text, "html.parser")
        return soup.get_text(separator = "\n", strip=True)
    return None

def send_email_to_api(sender, subject, body, timestamp, direction):
    body = body.strip().replace("\n", " ").replace("\r", " ")

    data = {
        "source": "gmail",
        "timestamp": f"{timestamp}",
        "content": f"{direction} an email from {sender} with title '{subject}'. The body of the email is {body}"
    }

    response = requests.post(API_URL_UPDATE, json=data)


def fetch_last_3_days_emails(service):
    query = "newer_than:3d"
    results = service.users().messages().list(userId='me', q=query, maxResults=100).execute()

    messages = results.get('messages', [])

    for message in messages:
        msg_id = message['id']
        msg = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()

        raw = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
        email_msg = message_from_bytes(raw)

        sender = email_msg.get('From', '')
        subject = decode_mime_header(email_msg.get('Subject', ''))
        body = extract_email_body(email_msg)

        if not body: continue
        
        timestamp = int(int(msg['internalDate'])/1000)
        direction = "sent" if "SENT" in msg.get("labelIds", []) else "received"

        send_email_to_api(sender, subject, body, timestamp, direction)

def fetch_new_emails(service, start_time):
    inbox_msgs = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute().get('messages', [])
    sent_msgs = service.users().messages().list(userId='me', labelIds=['SENT'], maxResults=10).execute().get('messages', [])
    all_messages = inbox_msgs + sent_msgs

    min_date = start_time
    max_date = min_date

    for i, message in enumerate(all_messages):
        msg_id = message['id']
        msg = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
        
        msg_timestamp = int(int(msg['internalDate'])/1000)

        if msg_timestamp < min_date:
            continue

        if msg_timestamp > max_date:
            max_date = msg_timestamp

        raw = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
        email_msg = message_from_bytes(raw)

        sender = email_msg.get('From', '')
        subject = decode_mime_header(email_msg.get('Subject', ''))
        body = extract_email_body(email_msg)
        
        if not body: continue

        timestamp = datetime.now().timestamp()
        direction = "sent" if "SENT" in msg.get("labelIds", []) else "received"

        send_email_to_api(sender, subject, body, timestamp, direction)

    return max_date

def main(poll_interval=1.0):
    service = authenticate()

    fetch_last_3_days_emails(service)

    last_fetched_timestamp = datetime.now().timestamp()

    while True:
        last_fetched_timestamp = fetch_new_emails(service, last_fetched_timestamp)
        time.sleep(poll_interval)

if __name__ == '__main__':
    main(poll_interval=60 * 5)
