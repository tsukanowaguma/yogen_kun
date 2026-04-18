import os
import datetime
# sys を追加（Pylanceにパスを教えるため）
import sys

# 1. 最初にパスを通す（重要）
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 2. 標準ライブラリ以外のインポートをまとめる
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# 3. 自分の作ったモジュールをインポート（1箇所に絞る）
from src.mail_sender import send_gmail

# --- 以下、関数定義 ---
# (ClientOptions は使っていないならインポートから消してOK)

# カレンダー読み取り専用スコープ
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    creds = None
    # 認証情報の保存ファイル
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # 有効な認証情報がない場合はログイン
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            # Docker環境ではブラウザが開けないため、ローカルで実行してtoken.jsonを作る必要があります
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

from src.mail_sender import send_gmail

def main():
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    # 送信用のテキストを作成
    if not events:
        mail_content = "今日の予定はありません。"
    else:
        content_lines = ["今日の予定一覧:"]
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event['summary']
            content_lines.append(f"・{start} | {summary}")
        mail_content = "\n".join(content_lines)

    # ターミナルに表示しつつ、メール送信
    print(mail_content)
    send_gmail("【YouGenKun】本日の予定通知", mail_content)

if __name__ == '__main__':
    main()