from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    FlexMessage,
    FlexBubble,
    FlexBox,
    FlexText,
)

def push_notification(line_id: str, title: str, content: str) -> None:
    from webhook import configuration
    with ApiClient(configuration) as client:
        line_bot_api = MessagingApi(client)
        line_bot_api.push_message(
            PushMessageRequest(
                to=line_id,
                messages=[
                    FlexMessage(
                        altText="Notification",
                        contents=FlexBubble(
                            header=FlexBox(layout="vertical", contents=[
                                FlexText(text=title, weight="bold", size="xl"),
                            ]),
                            body=FlexBox(layout="vertical", contents=[
                                FlexText(text=content, weight="regular"),
                            ]),
                        )
                    ),
                ],
            )
        )
