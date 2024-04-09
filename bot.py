# Импортируем необходимые классы.
import configparser
import logging
import time

from telegram.ext import Application, MessageHandler, filters, CommandHandler

from tg_chat_ai_bot.chat_gpt import GetResponse
from tg_chat_ai_bot.yandex_speechkit import synthesize

config = configparser.ConfigParser()
config.read('cfg.ini')

BOT_TOKEN = config['TELEGRAM']['BOT_TOKEN']

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! О чем сегодня поболтаем?",
    )


async def text_answer(update, context):
    await update.message.reply_text(f'{await GetResponse(update.message.text)}')


async def voice_answer(update, context):
    res = synthesize(text=update.message.text, chat_id=update.effective_message.chat_id,
                     export_path=f'voice/{time.time()}.ogg')
    await update.message.reply_voice(res[0])


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    text_handler = MessageHandler(filters.TEXT, text_answer)
    voice_handler = MessageHandler(filters.TEXT, voice_answer)
    application.add_handler(text_handler)
    application.add_handler(voice_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
