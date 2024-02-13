import os
import vk_api
import requests

from dialogflow_utils import get_dialogflow_respons
from google.cloud import dialogflow
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from google.protobuf.json_format import MessageToJson


VK_TOKEN_GROUP = os.getenv("VK_TOKEN_GROUP")
DIALOGFLOW_JSON_KEY = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PROJECT_ID = os.environ["DIALOG_FLOW_GOOGLE_PROJECT_ID"]


def send_telegram_alert(message):
    token = os.getenv("TOKEN_TG_BOT")
    chat_id = os.getenv("ADMIN_CHAT_ID")
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    params = {
        'chat_id': chat_id,
        'parse_mode': 'Markdown',
        'text': message
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    vk_session = vk_api.VkApi(token=VK_TOKEN_GROUP)
    vk_api = vk_session.get_api()
    dialogflow_session_client = dialogflow.SessionsClient()
    load_dotenv()
    try:
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                session_id = str(event.user_id)
                user_message = event.text
                dialogflow_response = get_dialogflow_respons(os.environ["GOOGLE_APPLICATION_CREDENTIALS"], user_message, session_id)
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
