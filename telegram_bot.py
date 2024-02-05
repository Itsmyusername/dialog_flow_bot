import logging
import os

from dotenv import load_dotenv
from google.cloud import dialogflow
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


load_dotenv()
TOKEN=os.environ["TOKEN_TG_BOT"]
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(request={"session": session, "query_input": query_input})

    return response.query_result.fulfillment_text

def reply_to_user(update: Update, context: CallbackContext):
    project_id = os.environ["DIALOG_FLOW_GOOGLE_PROJECT_ID"]
    session_id = str(update.message.chat_id)
    text = update.message.text
    language_code = "ru"

    response_text = detect_intent_texts(project_id, session_id, text, language_code)
    update.message.reply_text(response_text)

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    chat_id = os.getenv("ADMIN_CHAT_ID")
    text = f"Произошла ошибка: {context.error}"
    context.bot.send_message(chat_id=chat_id, text=text)


def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_to_user))
    dispatcher.add_error_handler(error_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
