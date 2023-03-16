from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging


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
