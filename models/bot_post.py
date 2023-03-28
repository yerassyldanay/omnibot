import content
import re


from constants import ParseMode, STATE, logger, KEY_COMMAND
from telegram import Update

from telegram.ext import (
    
    ContextTypes, 
   
)
from models.static_methods import StaticMethodsBot


class BotPost(StaticMethodsBot):
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
