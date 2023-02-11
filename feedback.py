from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
)

from pprint import pprint

import asyncio


TELEGRAM_BOT_STORAGE_TOKEN = "5907999364:AAFw6w6rmYyAhH2i2UkPYT6jfa6ytvCA-pY"

# Update(message=Message(channel_chat_created=False, chat=Chat(first_name='Yerassyl', id=420451657, type=<ChatType.PRIVATE>, username='yerassyl_danay'), date=datetime.datetime(2023, 1, 31, 19, 28, 39, tzinfo=<UTC>), delete_chat_photo=False, entities=(MessageEntity(length=6, offset=0, type=<MessageEntityType.BOT_COMMAND>),), from_user=User(first_name='Yerassyl', id=420451657, is_bot=False, language_code='ru', username='yerassyl_danay'), group_chat_created=False, message_id=1, supergroup_chat_created=False, text='/start'), update_id=944534786)
# Update(message=Message(channel_chat_created=False, chat=Chat(first_name='Assilkhan', id=420353277, last_name='Amankhan 💡', type=<ChatType.PRIVATE>, username='assilkhan_amankhan'), date=datetime.datetime(2023, 1, 31, 19, 28, 41, tzinfo=<UTC>), delete_chat_photo=False, entities=(MessageEntity(length=6, offset=0, type=<MessageEntityType.BOT_COMMAND>),), from_user=User(first_name='Assilkhan', id=420353277, is_bot=False, language_code='en', last_name='Amankhan 💡', username='assilkhan_amankhan'), group_chat_created=False, message_id=2, supergroup_chat_created=False, text='/start'), update_id=944534787)

class FeedbackStorage:
    def __init__(self) -> None:
        self.bot = self.bot = Bot(TELEGRAM_BOT_STORAGE_TOKEN)
        self.application = ApplicationBuilder().token(TELEGRAM_BOT_STORAGE_TOKEN).build()
        self.chat_ids = [
            '420451657',
            '420353277'
        ]

        self.application.add_handler(CommandHandler("start", self.start))

    async def send(self, text: str):
        for chat_id in self.chat_ids:
            await self.bot.send_message(
                chat_id=chat_id, 
                text=text,
                parse_mode="HTML"
            )

    def run(self):
        self.application.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pprint(update)

    async def __close(self):
        return asyncio.gather(self.application.shutdown())

    def close(self):
        asyncio.run(self.__close())


if __name__ == '__main__':
    app = FeedbackStorage()
    try:
        app.run()
    except Exception as ex:
        print(ex)
    finally:
        app.close()
