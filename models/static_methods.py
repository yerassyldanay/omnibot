from telegram.ext import (
    
    ContextTypes, 
   
)
from telegram import Update
import content
from constants import ParseMode, Keyboard, STATE, logger, KEY_COMMAND
import datetime
from translator.translator import TranslatorBot
from gpt.gpt import OpenAIChatGPT 
from config import gpt_token
from feedback import FeedbackStorage

class StaticMethodsBot:
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
            'assilkhan_amankhan': '',
            'tanat443': '' 
        }

    async def ask_gpt(self, text: str) -> str:
        self.gpt = OpenAIChatGPT(gpt_token)
        return await self.gpt.generate_response(text)

    async def write(self, user_info: dict, question: str, answer: str, typeof: str):
        self.storage = FeedbackStorage()
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