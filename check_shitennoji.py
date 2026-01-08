import requests
import hashlib
import json
import csv
import os
import smtplib
from email.mime.text import MIMEText

CSV_FILE = "schools.csv"
HASH_FILE = "last_hash.json"

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
TO_EMAIL = os.environ["TO_EMAIL"]

def load_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_hashes(data):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def send_mail(message):
    msg = MIMEText(message)
    msg["Subject"] = "小学校サイト更新通知"
    msg["From"] = GMAIL_USER
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)

def main():
    old_hashes = load_hashes()
    new_hashes = {}
    updates = []

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["school_name"]
            url = row["url"]

            r = requests.get(url, timeout=30)
            r.raise_for_status()

            h = get_hash(r.text)
            new_hashes[name] = h

            if old_hashes.get(name) and old_hashes[name] != h:
                updates.append(f"{name}\n{url}")

    save_hashes(new_hashes)

    if updates:
        send_mail("\n\n".join(updates))

if __name__ == "__main__":
    main()
