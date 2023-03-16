import content
from constants import ParseMode, Keyboard, STATE
from telegram.ext import (
    
    ContextTypes, 
   
)
from telegram import Update


class BotGuide:
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

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=self.get_text(content.HELP, context)
        )
        return STATE.NEWPOST