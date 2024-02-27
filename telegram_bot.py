import logging
import os

from dotenv import load_dotenv
from google.cloud import dialogflow
from dialogflow_utils import get_dialogflow_response
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


logger = logging.getLogger(__name__)


def extract_data_from_query_result(query_result):
    parameters = query_result.parameters
    extracted_parameters = {}
    for param, value in parameters.items():
        extracted_parameters[param] = value.string_value if value.string_value else value
    return extracted_parameters


def reply_to_user(update: Update, context: CallbackContext):
    project_id = os.environ["DIALOG_FLOW_GOOGLE_PROJECT_ID"]
    session_id = str(update.message.chat_id)
    text = update.message.text
    language_code = "ru"
    response = get_dialogflow_response(project_id, session_id, text, language_code)
    # Убедитесь, что здесь вы обращаетесь к атрибуту fulfillment_text объекта response.query_result
    response_text = response.fulfillment_text
    update.message.reply_text(response_text)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    chat_id = os.getenv("ADMIN_CHAT_ID")
    text = f"Произошла ошибка: {context.error}"
    context.bot.send_message(chat_id=chat_id, text=text)


def main() -> None:
    load_dotenv()
    TOKEN=os.environ["TOKEN_TG_BOT"]
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_to_user))
    dispatcher.add_error_handler(error_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
