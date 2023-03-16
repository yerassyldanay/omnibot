import os
import asyncio
from pprint import pprint

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, Chat
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
from feedback import FeedbackStorage
from example import TelegramBotExample
from gpt.gpt import OpenAIChatGPT
from constants import  STATE

from models.bot_post import BotPost
from models.bot_guide import BotGuide
from models.bot_feedback import BotFeedback
from models.static_methods import StaticMethodsBot

import time

# import openai
# openai.api_key = CHAT_GPT_API_KEY
from config import gpt_token, bot_token


class Application(BotPost, BotGuide, BotFeedback, StaticMethodsBot ):
    def __init__(self) -> None:
        self.__persistence = PicklePersistence(filepath="arbitrarycallbackdatabot")
        self.bot = Bot(bot_token)
        self.application = ApplicationBuilder().persistence(self.__persistence).token(bot_token).concurrent_updates(True).build()
        self.gpt = OpenAIChatGPT(gpt_token)
        self.example = TelegramBotExample()
        self.__set_buttons__()
        super().__init__()

    def __set_buttons__(self):
        startCommand = CommandHandler("start", self.start)
        helpCommand = CommandHandler("help", self.help)
        feedbackCommand = CommandHandler("feedback", self.ask_feedback)
        askNewPostCommand = CommandHandler("new", self.ask_new_post)
        askAddContextCommand = CommandHandler("add", self.ask_add_context)
        exampleCommand = CommandHandler("example", self.get_example)

        messageNewPost = MessageHandler(filters.TEXT, self.new_post)
        messageAddContext = MessageHandler(filters.TEXT, self.add_context)
        messageFeedback = MessageHandler(filters.TEXT, self.handle_feedback)

        callbackChooseLanguage = CallbackQueryHandler(self.change_language, pattern='choose_language_*')
        callbackContentButton = CallbackQueryHandler(self.new_or_additional, pattern='button_content_*')
        callbackGetExample = CallbackQueryHandler(self.get_example, pattern='show_me_examples*')

        callbackLikedPost = CallbackQueryHandler(self.liked_the_post, pattern='button_post_like')
        callbackDislikedPost = CallbackQueryHandler(self.disliked_the_post, pattern='button_post_dislike')

        conversation = ConversationHandler(
            entry_points=[
                startCommand,
                feedbackCommand,
                helpCommand,
                askAddContextCommand,
                askNewPostCommand,
                exampleCommand,
                messageNewPost,
                askAddContextCommand,
                callbackContentButton,
                callbackLikedPost,
                callbackDislikedPost,
                callbackGetExample
            ],
            states={
                STATE.CHOOSE_LANGUAGE: [
                    feedbackCommand,
                    helpCommand,
                    startCommand,
                    exampleCommand,
                    callbackChooseLanguage,
                    callbackContentButton,
                    callbackLikedPost,
                    callbackDislikedPost,
                    callbackGetExample
                ],
                STATE.NEWPOST: [
                    askAddContextCommand,
                    askNewPostCommand,
                    feedbackCommand,
                    helpCommand,
                    startCommand,
                    exampleCommand,
                    messageNewPost,
                    callbackContentButton,
                    callbackLikedPost,
                    callbackDislikedPost,
                    callbackGetExample
                ],
                STATE.ADD_CONTEXT: [
                    feedbackCommand,
                    helpCommand,
                    startCommand,
                    exampleCommand,
                    messageAddContext,
                    callbackContentButton,
                    callbackLikedPost,
                    callbackDislikedPost,
                    callbackGetExample
                ],
                STATE.FEEDBACK: [
                    feedbackCommand,
                    helpCommand,
                    startCommand,
                    feedbackCommand,
                    askAddContextCommand,
                    askNewPostCommand,
                    exampleCommand,
                    messageFeedback,
                    callbackContentButton,
                    callbackLikedPost,
                    callbackDislikedPost,
                    callbackGetExample
                ],
            },
            fallbacks=[
                feedbackCommand,
                helpCommand,
                startCommand,
                exampleCommand,
            ]
        )
        self.application.add_handler(conversation)
        self.application.add_handler(CommandHandler("add", self.ask_add_context))
    

   
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
