from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import openai
from dotenv import load_dotenv

# 載入 .env 環境變數
load_dotenv()

# 讀取環境變數
LINE_TOKEN = os.getenv("LINE_TOKEN")
LINE_SECRET = os.getenv("LINE_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 初始化 Line Bot 和 OpenAI API
api = LineBotApi(LINE_TOKEN)
handler = WebhookHandler(LINE_SECRET)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

print('LINE_TOKEN', api)
print('LINE_SECRET', handler)
# 建立 Flask 應用程式
app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello():
    return "Hello, Line Bot is running on Render!"

@app.route("/", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("電子簽章錯誤, 請檢查密鑰是否正確？")
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print('處理')
    user_id = event.source.user_id
    text = event.message.text.strip()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {'role': 'system', 'content': '你是一個專門回答鳥類相關問題的人工智慧助手。請用專業且有趣的方式回答，並提供詳細的鳥類資訊，例如分類、生態、習性等。如果使用者問與鳥類無關的問題，請禮貌地引導回鳥類主題。'},
            {"role": "user", "content": text},
        ]
    )
    reply = response.choices[0].message.content
    api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
