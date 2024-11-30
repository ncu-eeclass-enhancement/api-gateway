import dotenv
import os

from flask import Flask, request, abort
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3 import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent, UserSource
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    FlexMessage,
    FlexBubble,
    FlexBox,
    FlexText,
    ReplyMessageRequest,
)

dotenv.load_dotenv()
LINE_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

configuration = Configuration(
    access_token = LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info(f'Request body: {body}')
    print(body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# Message event

@handler.add(MessageEvent)
def handle_message(event: MessageEvent):
    message: TextMessageContent = event.message
    source: UserSource = event.source
    print(source.user_id, message.id, message.text, message.type)
    with ApiClient(configuration) as client:
        line_bot_api = MessagingApi(client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[
                    FlexMessage(
                        altText="Notification",
                        contents=FlexBubble(
                                header=FlexBox(layout="vertical", contents=[
                                    FlexText(text="title", weight="bold", size="xl"),
                                ]),
                            body=FlexBox(layout="vertical", contents=[
                                FlexText(text="content", weight="regular"),
                            ]),
                        )
                    ),
                ]
            )
        )

if __name__ == '__main__':
    # push_notification("U264089909b88fa12e277ce5136393077",
    #                   "Hello", "Hello, world!")
    app.run(port=8000, host="0.0.0.0")