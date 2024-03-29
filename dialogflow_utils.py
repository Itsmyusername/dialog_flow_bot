from google.cloud import dialogflow_v2 as dialogflow


def get_dialogflow_response(project_id, session_id, text, language_code='ru-RU'):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        session=session, query_input=query_input
    )
    return response.query_result
