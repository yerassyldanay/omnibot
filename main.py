# omni
TELEGRAM_BOT_TOKEN = "5925005582:AAGmVJKdFfgjajayG2XJUMk2y3iRLPCOVME"
# shopify
# TELEGRAM_BOT_TOKEN = "5290714195:AAGXSBX-5KDTbGjC5XJzO08oR7vON1jtuuM"
CHAT_GPT_API_KEY = ''

import content
import asyncio
import datetime
import logging
from pprint import pprint

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
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

import time
# import openai
# openai.api_key = CHAT_GPT_API_KEY


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
    CONTENT_KAZ = InlineKeyboardMarkup.from_column(
        button_column=[
            InlineKeyboardButton('Жаңа пост жазу', callback_data='button_content_new'),
            InlineKeyboardButton('Алдыңғы постқа мәлімет қосу', callback_data='button_content_add'),
        ],
    )
    CONTENT_RUS = InlineKeyboardMarkup.from_column(
        button_column=[
            InlineKeyboardButton('Добавить новый пост', callback_data='button_content_new'),
            InlineKeyboardButton('Добавить доп. инфо к пред. посту', callback_data='button_content_add'),
        ],
    )

class Application:
    def __init__(self) -> None:
        self.__persistence = PicklePersistence(filepath="arbitrarycallbackdatabot")
        self.bot = Bot(TELEGRAM_BOT_TOKEN)
        self.application = ApplicationBuilder().persistence(self.__persistence).token(TELEGRAM_BOT_TOKEN).concurrent_updates(True).build()
        self.storage = FeedbackStorage()
        self.gpt = OpenAIChatGPT(CHAT_GPT_API_KEY)
        self.example = TelegramBotExample()
        self.__set_buttons__()

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

        conversation = ConversationHandler(
            entry_points=[
                startCommand,
                feedbackCommand,
                helpCommand,
                askAddContextCommand,
                askNewPostCommand,
                exampleCommand,
            ],
            states={
                STATE.CHOOSE_LANGUAGE: [
                    feedbackCommand,
                    helpCommand,
                    startCommand,
                    exampleCommand,
                    callbackChooseLanguage,
                    callbackContentButton,
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
                ],
                STATE.ADD_CONTEXT: [
                    feedbackCommand,
                    helpCommand,
                    startCommand,
                    exampleCommand,
                    messageAddContext,
                    callbackContentButton,
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

    async def test(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        bot = context.bot
        chat_id = update.message.chat_id
        
        # Send a new message
        message = await bot.send_message(chat_id=chat_id, text="Process running...")
        
        # Update the previous message
        await bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text="Process finished.")


    @staticmethod
    def get_content_button(context: ContextTypes.DEFAULT_TYPE):
        if context.user_data.get("language", content.KAZ) == content.KAZ:
            return Keyboard.CONTENT_KAZ
        return Keyboard.CONTENT_RUS

    @staticmethod
    def get_text(textDict: dict, context: ContextTypes.DEFAULT_TYPE):
        return textDict.get(context.user_data.get("language", ''), '')

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode=ParseMode.HTML, 
            text=content.START,
            reply_markup=Keyboard.LANG,
        )

        # default language 
        context.user_data["language"] = content.KAZ

        return STATE.CHOOSE_LANGUAGE

    async def change_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query

        language_chosen = query.data
        logger.info(f"user has chosen the language: '{language_chosen}'")

        context.user_data["language"] = content.KAZ
        if language_chosen == "choose_language_rus":
            context.user_data["language"] = content.RUS

        showed_popup = context.user_data.get('showed_popup', False)
        context.user_data['showed_popup'] = True

        popup_message = self.popup(context=context)
        if popup_message != '' and not showed_popup:
            await query.answer(
                text=popup_message,
                show_alert=True,
            )

        await query.edit_message_text(
            text=self.get_text(content.HELLO, context),
        )
        # await self.bot.send_message(chat_id=query.message.chat.id, text=self.get_text(content.HELLO, context))
        return STATE.NEWPOST

    async def new_or_additional(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query

        button_type = query.data
        logger.info(f"user has chosen button type: '{button_type}'")

        state = STATE.NEWPOST
        textDictionary = content.SEND_NEW_POST

        if button_type == 'button_content_add':
            state = STATE.ADD_CONTEXT
            textDictionary = content.ADD_CONTEXT

        popup_message = self.popup(context=context)
        if popup_message != '':
            await query.answer(
                text=popup_message,
            )

        await self.bot.send_message(
            chat_id=query.message.chat.id, 
            text=self.get_text(textDictionary, context),
        )
        return state

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

    async def ask_new_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.hit_limit(context=context, incr=0):
            await update.message.reply_text(
                text=self.get_text(content.HIT_LIMIT, context)
            )
            return

        await update.message.reply_text(
            text=self.get_text(content.SEND_NEW_POST, context)
        )
        logger.info(f"received /new command from {update.message.from_user.username}")
        return STATE.NEWPOST

    async def new_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.user_in_vip_list(update=update) and self.hit_limit(context=context, incr=1):
            await update.message.reply_text(
                text=self.get_text(content.HIT_LIMIT, context)
            )
            return

        bot = context.bot
        chat_id = update.message.chat_id
        
        # Send a new message 'process is running'
        message = await bot.send_message(chat_id=chat_id, text=self.get_text(content.PROCESS_RUNNING, context))
        logger.info(f"user {update.message.from_user.username} new {update.message.text}")

        # adding . to the end of the text if there is no any ./!/?
        text_message = self.remove_command(update.message.text.strip(), '/new')
        text_message = self.add_puntuation(text_message)

        # storing data in a storage
        context.user_data['posts'] = text_message
        logger.info(f"post={text_message}")

        response = await self.get_translator(context.user_data["language"], "en").wrapper(text_message)
        logger.info(f"translator {response}")

        response = await self.ask_gpt(response)
        logger.info(f"response from GPT {response}")

        if response == 'ERROR':
            await bot.edit_message_text(
                chat_id=chat_id, 
                message_id=message.message_id, 
                text=self.get_text(textDict=content.EXCEPTION, context=context),
            )
            await self.write(
                username=update.message.from_user.username,
                question=text_message,
                answer='',
                typeof='new',
            )
            return
        
        response = await self.get_translator("en", context.user_data["language"]).wrapper(response)
        logger.info(f"response from google translator (to original language) {response}")

        logger.info(f'user language was {context.user_data["language"]}')

        await bot.edit_message_text(
            chat_id=chat_id, 
            message_id=message.message_id, 
            text=response,
            reply_markup=self.get_content_button(context=context)
        )

        await self.write(
            username=update.message.from_user.username,
            question=text_message,
            answer=response,
            typeof='new',
        )

        return

    async def ask_add_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.hit_limit(context=context, incr=0):
            await update.message.reply_text(
                text=self.get_text(content.HIT_LIMIT, context)
            )
            return

        await update.message.reply_text(
            text=self.get_text(content.ADD_CONTEXT, context)
        )
        logger.info(f"user {update.message.from_user.username} send /add command without text")
        return STATE.ADD_CONTEXT

    async def add_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE):        
        if not self.user_in_vip_list(update=update) and self.hit_limit(context=context, incr=1):
            await update.message.reply_text(
                text=self.get_text(content.HIT_LIMIT, context)
            )
            return

        bot = context.bot
        chat_id = update.message.chat_id
        
        # Send a new message 'process is running'
        message = await bot.send_message(chat_id=chat_id, text=self.get_text(content.PROCESS_RUNNING, context))

        # adding . to the end of the text if there is no any ./!/?
        text_message = update.message.text.strip()
        text_message = self.add_puntuation(text_message)
        
        user_input = text_message
        logger.info(f"user {update.message.from_user.username} send add info '{user_input} ...'")

        response = await self.get_translator(context.user_data["language"], "en").wrapper(user_input)
        logger.info(f"google translator response {response}")

        response = context.user_data.get("posts", "") + " " + response
        context.user_data['posts'] = response

        response = await self.ask_gpt(response)
        logger.info(f"response from GPT {response}")

        if response == 'ERROR':
            await bot.edit_message_text(
                chat_id=chat_id, 
                message_id=message.message_id, 
                text=self.get_text(textDict=content.EXCEPTION, context=context),
            )
            await self.write(
                username=update.message.from_user.username,
                question=text_message,
                answer='',
                typeof='add',
            )
            return

        response = await self.get_translator("en", context.user_data["language"]).wrapper(response)
        logger.info(f"response from google translator (to original language) {response}")

        await bot.edit_message_text(
            chat_id=chat_id, 
            message_id=message.message_id, 
            text=response,
            reply_markup=self.get_content_button(context=context)
        )

        await self.write(
            username=update.message.from_user.username,
            question=text_message,
            answer=response,
            typeof='add',
        )

        logger.info(f'user language was {context.user_data["language"]}')

        return STATE.NEWPOST

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=self.get_text(content.HELP, context)
        )
        return STATE.NEWPOST

    async def ask_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode=ParseMode.HTML, 
            text=self.get_text(content.FEEDBACK, context)
        )
        return STATE.FEEDBACK

    async def handle_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=self.get_text(content.THANKS_FOR_FEEDBACK, context),
        )
        await self.storage.send(f'''user: {update.message.from_user.username}
feedback: {update.message.text}
        ''')
        return STATE.NEWPOST

    async def ask_gpt(self, text: str) -> str:
        return await self.gpt.generate_response(text)

    @staticmethod
    def get_translator(from_lang, to_lang: str):
        return TranslatorBot(from_lang=from_lang, to_lang=to_lang)

    @staticmethod
    def hit_limit(context: ContextTypes.DEFAULT_TYPE, incr: int = 0) -> bool:
        if 'limit' not in context.user_data:
            context.user_data['limit'] = dict()

        keyDate = datetime.datetime.now().strftime("%d.%m.%Y")
        if keyDate not in context.user_data['limit']:
             context.user_data['limit'] = dict()
             
        context.user_data['limit'][keyDate] = context.user_data['limit'].get(keyDate, 0) + incr
        return context.user_data['limit'].get(keyDate, 0) >= 7

    def popup(self, context: ContextTypes.DEFAULT_TYPE) -> str:
        if 6 - self.get_limit(context=context) <= 0:
            return ''
        
        if context.user_data.get("language", content.KAZ) == content.KAZ:
            return f'Сіз бүгінге {6 - self.get_limit(context=context)} рет сұрай аласыз'
        
        return f'Вы можете обращаться {6 - self.get_limit(context=context)} раз за день'

    @staticmethod
    def get_limit(context: ContextTypes.DEFAULT_TYPE) -> int:
        keyDate = datetime.datetime.now().strftime("%d.%m.%Y")
        return context.user_data.get('limit', dict()).get(keyDate, 0)

    @staticmethod
    def user_in_vip_list(update: Update):
        return update.message.chat.username in {
            'yerassyl_danay': '',
            'assilkhan_amankhan': ''
        }

    async def get_example(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        index = context.user_data.get('example', 0)
        context.user_data['example'] = self.example.increment(index=index)
        result = self.example.get(index=index, lang=context.user_data.get("language", content.KAZ))
        
        await update.message.reply_text(
            text=result,
            parse_mode=ParseMode.HTML,
        )

    async def write(self, username: str, question: str, answer: str, typeof: str):
        # df = pd.DataFrame(
        #     {
        #         'username': [username],
        #         'question': [question],
        #         'answer': [answer],
        #         'date': [datetime.datetime.now().strftime("%d.%m.%Y")],
        #         'type': [typeof],
        #     }
        # )

        # filename = f'./logs/{datetime.datetime.now().strftime("%d.%m.%Y")}.xlsx'

        # # open the existing Excel file in append mode
        # book = openpyxl.load_workbook(filename)
        # writer = pd.ExcelWriter(filename, engine='openpyxl') 
        # writer.book = book

        # # write the dataframe to the existing Excel file
        # df.to_excel(writer, index=False, startrow=writer.sheets['feedback'].max_row)

        # # save the changes
        # writer.save()

        await self.storage.send(f'''username: {username}
type: {typeof},
question: {question}''')

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
