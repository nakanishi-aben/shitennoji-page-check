import requests
import hashlib
import os
import smtplib
from email.mime.text import MIMEText

URL = "https://www.shitennojigakuen.ed.jp/primary/adinfo/"
HASH_FILE = "last_hash.txt"

res = requests.get(URL, timeout=20)
res.raise_for_status()
html = res.text

current_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()

if os.path.exists(HASH_FILE):
    with open(HASH_FILE, "r") as f:
        last_hash = f.read().strip()
else:
    last_hash = ""

if current_hash != last_hash:
    from_addr = os.environ["MAIL_FROM"]
    to_addr   = os.environ["MAIL_TO"]
    password  = os.environ["MAIL_PASS"]

    msg = MIMEText(f"以下のページが更新されました。\n\n{URL}")
    msg["Subject"] = "【更新通知】四天王寺学園小学校 入試・説明会情報"
    msg["From"] = from_addr
    msg["To"] = to_addr

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_addr, password)
        smtp.send_message(msg)

    with open(HASH_FILE, "w") as f:
        f.write(current_hash)

    print("更新あり → メール送信")
else:
    print("更新なし")
