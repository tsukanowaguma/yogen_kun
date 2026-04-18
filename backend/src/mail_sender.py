import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_gmail(subject, body):
    # .envから情報を取得
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    if not gmail_user or not gmail_password:
        print("エラー: GMAIL_USER または GMAIL_APP_PASSWORD が設定されていません。")
        return

    # メールの作成
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = gmail_user  # 自分宛に送信
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # SMTPサーバー（Gmail）に接続
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
        print("Gmailを送信しました。")
    except Exception as e:
        print(f"メール送信エラー: {e}")