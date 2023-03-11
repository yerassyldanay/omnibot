# omni
TELEGRAM_BOT_TOKEN = "5925005582:AAGmVJKdFfgjajayG2XJUMk2y3iRLPCOVME"
# shopify
# TELEGRAM_BOT_TOKEN = "5290714195:AAGXSBX-5KDTbGjC5XJzO08oR7vON1jtuuM"
# free version
# CHAT_GPT_API_KEY = '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'
# paid version
CHAT_GPT_API_KEY = ''

import re
import content
import asyncio
import datetime
import logging
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

import time
# import openai
# openai.api_key = CHAT_GPT_API_KEY

KEY_COMMAND = "COMMAND"

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

    CONTENT_KAZ = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Жауап ұнады', callback_data='button_post_like'),
                InlineKeyboardButton('Жауап нашар', callback_data='button_post_dislike')
            ],
            [
                InlineKeyboardButton('Жаңа пост жазу', callback_data='button_content_new')
            ],
            [
                InlineKeyboardButton('Алдыңғы постқа мәлімет қосу', callback_data='button_content_add'),
            ]
        ]
    )

    CONTENT_RUS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Ответ нравится', callback_data='button_post_like'),
                InlineKeyboardButton('Ответ не нравится', callback_data='button_post_dislike')
            ],
            [
                InlineKeyboardButton('Добавить новый пост', callback_data='button_content_new')
            ],
            [
                InlineKeyboardButton('Добавить доп. инфо к пред. посту', callback_data='button_content_add'),
            ],
        ]
    )

    EXMPLES_KAZ = InlineKeyboardMarkup.from_row([
        InlineKeyboardButton('Мысалдар көрсет', callback_data='show_me_examples'),
    ])

    EXMPLES_RUS = InlineKeyboardMarkup.from_row([
        InlineKeyboardButton('Покажи примеры', callback_data='show_me_examples'),
    ])


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

    @staticmethod
    def get_user_info(update: Update) -> dict:
        user_info = dict()
        chat = None
        if hasattr(update, 'callback_query') and update.callback_query != None \
            and hasattr(update.callback_query, 'message') and update.callback_query.message != None \
            and hasattr(update.callback_query.message, 'chat') and update.callback_query.message.chat != None:
            chat = update.callback_query.message.chat
        elif update.message != None and update.message.chat != None:
            chat = update.message.chat
        else:
            return user_info

        if chat.first_name:
            user_info['first_name'] = chat.first_name
        
        if chat.username:
            user_info['username'] = chat.username
        
        if chat.id:
            user_info['id'] = chat.id

        if chat.type:
            user_info['type'] = chat.type

        return user_info

    @staticmethod
    def map_to_str(d: dict, sep: str = '') -> str:
        result = []
        for key, value in d.items():
            result.append(f'{key}={value}{sep} ')
        return ''.join(result)
    
    @staticmethod
    def log(d: dict, add: dict = {}):
        result = []
        for key, value in d.items():
            result.append(f'{key}={value}')

        for key, value in add.items():
            result.append(f'{key}={value}')

        logger.info('; '.join(result))

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

        user_info = self.get_user_info(update=update)
        user_info_copy = user_info.copy()
        user_info_copy.update({
            "COMMAND": "/start"
        })
        self.log(user_info_copy)

        # default language 
        context.user_data["language"] = content.KAZ

        return STATE.CHOOSE_LANGUAGE
    
    async def change_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        
        user_info = self.get_user_info(update=update)

        query = update.callback_query

        language_chosen = query.data
        
        self.log(user_info, { KEY_COMMAND: "change_language", "lang": language_chosen})

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

        example_button = Keyboard.EXMPLES_KAZ
        if context.user_data["language"] == content.RUS:
            example_button = Keyboard.EXMPLES_RUS

        await query.edit_message_text(
            text=self.get_text(content.HELLO, context),
            parse_mode=ParseMode.HTML,
            reply_markup=example_button,
        )
        # await self.bot.send_message(chat_id=query.message.chat.id, text=self.get_text(content.HELLO, context))
        return STATE.NEWPOST

    async def liked_the_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        query.answer()

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=self.get_text(content.THANKS_FOR_FEEDBACK, context),
        )

        user_info = self.get_user_info(update)
        user_info.update({"action": "liked the post"})

        await self.storage.sendKeyValues(
            dictionary=user_info, 
        )

        return STATE.NEWPOST

    async def disliked_the_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        query.answer()

        user_info = self.get_user_info(update)

        keep_attention_text = '''Сорри, если не оправдал ваши ожидания. Возможно, вы имели в виду:'''
        if context.user_data["language"] == content.KAZ:
            keep_attention_text = '''Жауабым көңіліңізден шықпаса, сорри. Мүмкін, сіз мынаны меңзедіңіз:'''
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=keep_attention_text,
        )

        user_info = self.get_user_info(update)
        await self.storage.sendKeyValues(
            user_info, {"action": "disliked the post"}
        )

        request_for_question = f'''I have a following question in a below paragraph and I doubt it is complete. In order for you, ChatGPT, to give me a thorough and correct answer on this topic, how should I formulate my question? Return only the question
        
{context.user_data['posts']}'''

        self.log(user_info, { KEY_COMMAND: "disliked_the_post", "request_for_question": request_for_question})

        response = await self.ask_gpt(request_for_question)
        logger.info(f"response from GPT {response}")

        if response == 'ERROR':
            return
        
        response = await self.get_translator("en", context.user_data["language"]).wrapper(response)
        
        self.log(user_info, { KEY_COMMAND: "disliked_the_post", "get_translator_1": response})

        # prettify response 
        response = response.lstrip(" \n!.,;:'\"-")

        final_text = f'''<pre>{response}</pre>'''
        if context.user_data["language"] == content.KAZ:
            final_text = f'''<pre>{response}</pre>'''

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=final_text,
            parse_mode=ParseMode.HTML
        )
        return STATE.NEWPOST

    async def new_or_additional(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        user_info = self.get_user_info(update)

        query = update.callback_query

        button_type = query.data

        self.log(user_info, { KEY_COMMAND: "new_or_additional", "button_type": button_type})

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
        
        user_info = self.get_user_info(update)
        self.log(user_info, {KEY_COMMAND: "ask_new_post"})

        if self.hit_limit(context=context, incr=0):
            await update.message.reply_text(
                text=self.get_text(content.HIT_LIMIT, context)
            )
            return

        text_message = update.message.text.strip()
        if text_message != "/new":
            return await self.new_post(update=update, context=context)

        await update.message.reply_text(
            text=self.get_text(content.SEND_NEW_POST, context)
        )
        return STATE.NEWPOST

    async def new_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        user_info = self.get_user_info(update)
        
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
        self.log(user_info, {"TYPE": "added new post", "text": update.message.text})

        # adding . to the end of the text if there is no any ./!/?
        text_message = self.remove_command(update.message.text.strip(), '/new')
        text_message = self.add_puntuation(text_message)

        response = await self.get_translator(context.user_data["language"], "en").wrapper(text_message)
        logger.info(f"translator {response}")
        self.log(user_info, {"TYPE": "get_translator_1", "response": response})

        # storing data in a storage
        context.user_data['posts'] = response
        self.log(user_info, {"TYPE": "stored in the context", "context": response})

        response = await self.ask_gpt(response)
        self.log(user_info, {"TYPE": "ask_gpt", "response": response})

        if response == 'ERROR':
            await bot.edit_message_text(
                chat_id=chat_id, 
                message_id=message.message_id, 
                text=self.get_text(textDict=content.EXCEPTION, context=context),
            )
            await self.write(
                user_info=user_info,
                question=text_message,
                answer='',
                typeof='new',
            )
            return
        
        response = await self.get_translator("en", context.user_data["language"]).wrapper(response)
        self.log(user_info, {"TYPE": "get_translator_2", "response": response, "lang": context.user_data["language"]})

        response = re.sub("[\n]{1,}", "\n", re.sub(r"</b>+|<b>+","\n",response))

        await bot.edit_message_text(
            chat_id=chat_id, 
            message_id=message.message_id, 
            text=response,
            reply_markup=self.get_content_button(context=context),
            parse_mode=ParseMode.HTML
        )

        await self.write(
            user_info=user_info,
            question=text_message,
            answer='',
            typeof='new',
        )

        return

    async def ask_add_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.hit_limit(context=context, incr=0):
            await update.message.reply_text(
                text=self.get_text(content.HIT_LIMIT, context)
            )
            return

        text_message = update.message.text.strip()
        if text_message != "/add":
            return await self.add_context(update=update, context=context)

        await update.message.reply_text(
            text=self.get_text(content.ADD_CONTEXT, context)
        )
        logger.info(f"user {update.message.from_user.username} send /add command without text")
        return STATE.ADD_CONTEXT

    async def add_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE):        
        
        user_info = self.get_user_info(update)

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
        text_message = self.remove_command(update.message.text.strip(), '/new')
        text_message = self.add_puntuation(text_message)
        
        user_input = text_message
        self.log(user_info, {"TYPE": "added context", "added_context": text_message, "lang": context.user_data["language"]})

        response = await self.get_translator(context.user_data["language"], "en").wrapper(user_input)
        self.log(user_info, {"TYPE": "get_translator_1", "response": response, "lang": context.user_data["language"]})

        response = context.user_data.get("posts", "") + " " + response
        context.user_data['posts'] = response

        response = await self.ask_gpt(response)
        self.log(user_info, {"TYPE": "ask_gpt", "response": response, "lang": context.user_data["language"]})

        if response == 'ERROR':
            await bot.edit_message_text(
                chat_id=chat_id, 
                message_id=message.message_id, 
                text=self.get_text(textDict=content.EXCEPTION, context=context),
            )
            await self.write(
                user_info=user_info,
                question=text_message,
                answer='',
                typeof='add',
            )
            return

        response = await self.get_translator("en", context.user_data["language"]).wrapper(response)
        self.log(user_info, {"TYPE": "get_translator_2", "response": response, "lang": context.user_data["language"]})

        response = re.sub("[\n]{1,}", "\n", re.sub(r"</b>+|<b>+","\n",response))

        await bot.edit_message_text(
            chat_id=chat_id, 
            message_id=message.message_id, 
            text=response,
            reply_markup=self.get_content_button(context=context),
            parse_mode=ParseMode.HTML
        )

        await self.write(
            user_info=user_info,
            question=text_message,
            answer='',
            typeof='add',
        )

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
        user_info = self.get_user_info(update=update)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=self.get_text(content.THANKS_FOR_FEEDBACK, context),
        )

        user_info["feedback"] = update.message.text
        
        result = []
        for key, value in user_info.items():
            result.append(f'''{key}={value}
''')
        await self.storage.send(''.join(result))

        return STATE.NEWPOST

    async def ask_gpt(self, text: str) -> str:
        return await self.gpt.generate_response(text)

    @staticmethod
    def get_translator(from_lang, to_lang: str):
        return TranslatorBot(from_lang=from_lang, to_lang=to_lang, use_proxy=True)

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
        
        example_button = Keyboard.EXMPLES_KAZ
        if context.user_data["language"] == content.RUS:
            example_button = Keyboard.EXMPLES_RUS

        if update != None and update.message != None:
            await update.message.reply_text(
                text=result,
                parse_mode=ParseMode.HTML,
                reply_markup=example_button,
            )
            return STATE.NEWPOST
            
        query = update.callback_query
        await query.answer()
        await self.bot.send_message(
            chat_id=query.message.chat.id, 
            text=result,
            parse_mode=ParseMode.HTML,
            reply_markup=example_button,
        )
        return STATE.NEWPOST


    async def write(self, user_info: dict, question: str, answer: str, typeof: str):
        result = []
        for key, value in user_info.items():
            result.append(f'''{key}: {value}
''')
        
        result.extend([
            f'''type: {typeof}
''',
            f'''question: {question}
''',
        ])

        await self.storage.send(''.join(result))

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
