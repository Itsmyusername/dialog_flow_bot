import requests
import argparse
import json
import os

from dotenv import load_dotenv
from google.cloud import dialogflow_v2 as dialogflow


url = "https://dvmn.org/media/filer_public/a7/db/a7db66c0-1259-4dac-9726-2d1fa9c44f20/questions.json"
response = requests.get(url)
questions_data = response.json()


def download_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []

    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )

    response = intents_client.create_intent(request={"parent": parent, "intent": intent})
    print("Intent created: {}".format(response))


def main(data_url):
    questions_data = download_data(data_url)

    project_id = os.environ["DIALOG_FLOW_GOOGLE_PROJECT_ID"]

    for intent_name, data in questions_data.items():
        questions = data["questions"]
        answer = data["answer"]

        create_intent(
            project_id=project_id,
            display_name=intent_name[:30],
            training_phrases_parts=questions,
            message_texts=[answer]
        )


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Download questions from a URL and create Dialogflow intents.")
    parser.add_argument("data_url", help="URL to the JSON file containing questions and answers.")

    args = parser.parse_args()
    main(args.data_url)
