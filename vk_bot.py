import os
import vk_api

from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow_v2 as dialogflow
from google.protobuf.json_format import MessageToJson


load_dotenv()
VK_TOKEN_GROUP = os.getenv("VK_TOKEN_GROUP")
DIALOGFLOW_JSON_KEY = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PROJECT_ID = "newagent-rxdx"

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


if __name__ == "__main__":
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
