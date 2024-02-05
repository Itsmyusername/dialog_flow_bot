import os
import vk_api
import requests

from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow_v2 as dialogflow
from google.protobuf.json_format import MessageToJson


load_dotenv()
VK_TOKEN_GROUP = os.getenv("VK_TOKEN_GROUP")
DIALOGFLOW_JSON_KEY = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PROJECT_ID = os.environ["DIALOG_FLOW_GOOGLE_PROJECT_ID"]

vk_session = vk_api.VkApi(token=VK_TOKEN_GROUP)
vk_api = vk_session.get_api()
dialogflow_session_client = dialogflow.SessionsClient()


def send_to_dialogflow(text, session_id):
    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow.TextInput(text=text, language_code="ru-RU")
    query_input = dialogflow.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(
        session=session, query_input=query_input
    )
    return response

def handle_message(event):
    session_id = str(event.user_id)
    user_message = event.text
    dialogflow_response = send_to_dialogflow(user_message, session_id)
    response_text = dialogflow_response.query_result.fulfillment_text
    vk_api.messages.send(
        user_id=event.user_id,
        message=response_text,
        random_id=event.random_id
    )

def send_telegram_alert(message):
    token = os.getenv("TOKEN_TG_BOT")
    chat_id = os.getenv("ADMIN_CHAT_ID")
    send_text = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message}'

    response = requests.get(send_text)
    return response.json()


if __name__ == "__main__":
    try:
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                session_id = str(event.user_id)
                user_message = event.text
                dialogflow_response = send_to_dialogflow(user_message, session_id)
                if not dialogflow_response.query_result.intent.is_fallback:
                    response_text = dialogflow_response.query_result.fulfillment_text
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message=response_text,
                        random_id=event.random_id
                        )
    except Exception as e:
        error_message = f"Произошла ошибка в боте VK: {e}"
        send_telegram_alert(error_message)
        raise e
