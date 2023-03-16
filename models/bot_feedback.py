import content
from constants import ParseMode, Keyboard, STATE, logger, KEY_COMMAND
from telegram.ext import (
    
    ContextTypes, 
   
)
from telegram import Update
from models.static_methods import StaticMethodsBot
from feedback import FeedbackStorage


class BotFeedback(StaticMethodsBot):
    def __init__(self) -> None:
        self.storage = FeedbackStorage()

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