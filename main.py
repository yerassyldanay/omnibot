TELEGRAM_BOT_TOKEN = "5925005582:AAEMpX64oLmKvY9CFEf3KVGPXdbMMXBCcRo"

import content
import asyncio
import logging
from pprint import pprint

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    ConversationHandler,
    CallbackQueryHandler,
    PicklePersistence,
    MessageHandler,
    filters
)
from translator.translator import TranslatorBot


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class ParseMode:
    MarkdownV2 = "MarkdownV2"
    HTML = "HTML"


class STATE:
    NEWPOST, ADD_CONTEXT, CHOOSE_LANGUAGE, FEEDBACK = range(4)


class Keyboard:
    LANG = InlineKeyboardMarkup.from_row([
        InlineKeyboardButton('қазақша', callback_data='choose_language_kaz'),
        InlineKeyboardButton('русский', callback_data='choose_language_rus'),
    ])


class Application:
    def __init__(self) -> None:
        self.translator = TranslatorBot("kk")
        self.__persistence = PicklePersistence(filepath="arbitrarycallbackdatabot")
        self.application = ApplicationBuilder().persistence(self.__persistence).token(TELEGRAM_BOT_TOKEN).build()
        self.__set_buttons__()

    def __set_buttons__(self):
        startCommand = CommandHandler("start", self.start)
        helpCommand = CommandHandler("help", self.help)
        feedbackCommand = CommandHandler("feedback", self.ask_feedback)
        askNewPostCommand = CommandHandler("new", self.ask_new_post)
        askAddContextCommand = CommandHandler("add", self.ask_add_context)

        messageNewPost = MessageHandler(filters.TEXT, self.new_post)
        messageAddContext = MessageHandler(filters.TEXT, self.add_context)
        messageFeedback = MessageHandler(filters.TEXT, self.handle_feedback)

        callbackChooseLanguage = CallbackQueryHandler(self.change_language)

        conversation = ConversationHandler(
            entry_points=[
                startCommand,
                feedbackCommand,
                helpCommand,
                askAddContextCommand,
                askNewPostCommand,
            ],
            states={
                STATE.CHOOSE_LANGUAGE: [
                    feedbackCommand,
                    helpCommand,
                    startCommand,
                    callbackChooseLanguage,
                ],
                STATE.NEWPOST: [
                    askAddContextCommand,
                    askNewPostCommand,
                    feedbackCommand,
                    helpCommand,
                    startCommand,
                    messageNewPost,
                ],
                STATE.ADD_CONTEXT: [
                    feedbackCommand,
                    helpCommand,
                    startCommand,
                    messageAddContext,
                ],
                STATE.FEEDBACK: [
                    feedbackCommand,
                    helpCommand,
                    startCommand,
                    messageFeedback
                ],
            },
            fallbacks=[
                feedbackCommand,
                helpCommand,
                startCommand
            ]
        )
        self.application.add_handler(conversation)
        self.application.add_handler(CommandHandler("add", self.ask_add_context))

    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode=ParseMode.HTML, 
            text=content.START,
            reply_markup=Keyboard.LANG,
        )

        # default language 
        context.user_data["language"] = "kaz"

        return STATE.CHOOSE_LANGUAGE

    @staticmethod
    async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query

        language_chosen = query.data
        logger.info(f"user has chosen the language: '{language_chosen}'")

        await query.answer()

        context.user_data["language"] = "kaz"
        if language_chosen == "choose_language_rus":
            context.user_data["language"] = "rus"

        await query.edit_message_text(
            text=content.SEND_NEW_POST,
        )
        return STATE.NEWPOST

    @staticmethod
    def remove_command(text, command: str) -> str:
        if text.startswith(command):
            text = text.replace(command, '', 1).strip()
        return text

    @staticmethod
    def add_puntuation(text: str) -> str:
        has_beautiful_end = text.endswith('.') or text.endswith('!') or text.endswith('?')
        if not has_beautiful_end:
            text = text + '.'
        return text

    @staticmethod
    def is_only_command(text_message, command: str) -> bool:
        if text_message == '/new':
            return True
        return False

    @staticmethod
    async def ask_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            text=content.SEND_NEW_POST,
        )
        logger.info(f"received /new command from {update.message.from_user.username}")
        return STATE.NEWPOST

    async def new_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"user {update.message.from_user.username} added a new post {update.message.text}")

        # adding . to the end of the text if there is no any ./!/?
        text_message = self.remove_command(update.message.text.strip(), '/new')
        text_message = self.add_puntuation(text_message)

        # storing data in a storage
        context.user_data['posts'] = text_message
        pprint(context.user_data)

        response = self.translator.translate(update.message.text)
        await update.message.reply_text(
            text=response,
        )

        # TODO gpt

        await update.message.reply_text(
            text=content.TO_ADD_CONTEXT,
        )

        return

    @staticmethod
    async def ask_add_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            text=content.ADD_CONTEXT,
        )
        logger.info(f"user {update.message.from_user.username} send /add command without text")
        return STATE.ADD_CONTEXT


    async def add_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text_sent = update.message.text.strip() 
        user_input = update.message.text.strip()
        logger.info(f"user {update.message.from_user.username} send add info '{text_sent[:20]} ...'")
        
        # adding . to the end of the text if there is no any ./!/?
        text_message = update.message.text.strip()
        # text_message = self.remove_command(text_message, '/new')
        text_message = self.add_puntuation(text_message)

        user_input = context.user_data.get("posts", "") + " " + user_input
        context.user_data['posts'] = user_input
        response = self.translator.translate(user_input)
        await update.message.reply_text(
            text=response,
        )

        # TODO gpt

        await update.message.reply_text(
            text=content.TO_ADD_CONTEXT,
        )

        return STATE.NEWPOST

    @staticmethod
    async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode=ParseMode.HTML, 
            text=content.HELP,
        )
        return STATE.NEWPOST

    async def ask_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode=ParseMode.HTML, 
            text=content.FEEDBACK,
        )
        return STATE.FEEDBACK

    @staticmethod
    async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode=ParseMode.HTML, 
            text="спасибо за фидбэк",
        )
        return STATE.NEWPOST

    def run(self):
        self.application.run_polling()

    async def __close(self):
        return asyncio.gather(self.application.shutdown())

    def close(self):
        asyncio.run(self.__close())
            

if __name__ == '__main__':
    app = Application()
    try:
        app.run()
    except Exception as ex:
        print(ex)
    finally:
        app.close()
