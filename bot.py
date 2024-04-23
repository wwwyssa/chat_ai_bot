# Импортируем необходимые классы.
import configparser
import logging
import time

from telegram.ext import Application, MessageHandler, filters, CommandHandler

from chat_gpt import GetResponse
from yandex_speechkit import synthesize

from data import db_session
from data.users import User

db_session.global_init("db/users.db")

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
    db_sess = db_session.create_session()
    if db_sess.query(User).filter(User.user_id == update.effective_message.chat_id).first() == None:
        print('NEW USER')
        user_db = User(
            user_id=update.effective_message.chat_id,
            is_admin=False,
            model="alexander",
            last_messages="",
            story="",
            listened=0,
        )
        db_sess.add(user_db)
        await update.message.reply_html(rf"Привет {user.mention_html()}! Ты здесь впервые, о чем сегодня поболтаем?")
        try:
            db_sess.commit()
            return
        except:
            db_sess.rollback()
            await update.message.reply_html(rf"Привет {user.mention_html()}! Попробуйте еще раз")
            return
    await update.message.reply_html(rf"Привет {user.mention_html()}! О чем сегодня поболтаем?")


def save_mem(user_id, text):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == user_id).first()
    user.story += text
    db_sess.commit()


async def text_answer(update, context):
    text = GetResponse(update.message.text, update.effective_message.chat_id)
    save_mem(update.effective_message.chat_id, f"{update.message.text}")
    await update.message.reply_text(f'{text}')


async def voice_answer(update, context):
    text = GetResponse(update.message.text, update.effective_message.chat_id)
    save_mem(update.effective_message.chat_id, f"{update.message.text}")
    res = synthesize(text=text, chat_id=update.effective_message.chat_id, export_path=f'voice/{time.time()}.ogg')
    await update.message.reply_voice(res[0])


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    voice_handler = MessageHandler(filters.TEXT, voice_answer)
    text_handler = MessageHandler(filters.TEXT, text_answer)
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
