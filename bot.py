# Импортируем необходимые классы.
import configparser
import logging
import time

from telegram.ext import Application, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
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
            db_sess.close()
            return
        except:
            db_sess.rollback()
            await update.message.reply_html(rf"Привет {user.mention_html()}! Попробуйте еще раз")
            return
    await update.message.reply_html(rf"Привет {user.mention_html()}! О чем сегодня поболтаем?")


async def choose(update, context):
    reply_keyboard = [['/voice', '/text']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_html(rf"Выбери то как ты хочешь, чтобы я отвечал:", reply_markup=markup)


async def ans_text(update, context):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == update.effective_message.chat_id).first()
    user.model = 'text'
    db_sess.commit()
    db_sess.close()
    await update.message.reply_html(rf"Выбран ответ текстом", reply_markup=ReplyKeyboardRemove())


async def ans_voice(update, context):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == update.effective_message.chat_id).first()
    user.model = 'voice'
    db_sess.commit()
    db_sess.close()
    await update.message.reply_html(rf"Выбран ответ голосом", reply_markup=ReplyKeyboardRemove())


def save_mem(user_id, text):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == user_id).first()
    user.story += text
    db_sess.commit()
    db_sess.close()


async def text_answer(chat_id, text_inp):
    text = GetResponse(text_inp, chat_id)
    save_mem(chat_id, f"{text}")
    return text


async def voice_answer(chat_id, text_inp):
    text = GetResponse(text_inp, chat_id)
    save_mem(chat_id, f"{text_inp}")
    res = synthesize(text=text, chat_id=chat_id, export_path=f'voice/{time.time()}.ogg')
    return res[0]


async def messages_handler(update, context):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == update.effective_message.chat_id).first()
    if user.model == 'text':
        ans = await text_answer(update.effective_message.chat_id, update.message.text)
        await update.message.reply_text(f'{ans}')
    else:
        ans = await voice_answer(update.effective_message.chat_id, update.message.text)
        await update.message.reply_voice(ans)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("choose", choose))
    message_handler = MessageHandler(filters.TEXT, messages_handler)
    application.add_handler(message_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
