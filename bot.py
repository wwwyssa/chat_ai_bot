import configparser
import time

from telegram.ext import Application, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from chat_gpt import GetResponse, save_memory
from yandex_speechkit import synthesize

from data import db_session
from data.users import User

db_session.global_init("db/users.db")

config = configparser.ConfigParser()
config.read('cfg.ini')

BOT_TOKEN = config['TELEGRAM']['BOT_TOKEN']


# /start - регистрация в боте
async def start(update, context):
    user = update.effective_user
    db_sess = db_session.create_session()
    if db_sess.query(User).filter(User.user_id == update.effective_message.chat_id).first() == None:
        user_db = User(
            user_id=update.effective_message.chat_id,
            is_admin=False,
            model="text",
            last_messages="",
            story="",
            banned=False
        )
        db_sess.add(user_db)
        await update.message.reply_html(
            rf"Привет {user.mention_html()}! Ты здесь впервые, о чем сегодня поболтаем? Доступные команды: /choose - выбор формата ответа бота"
        )
        try:
            db_sess.commit()
            db_sess.close()
            return
        except:
            db_sess.rollback()
            await update.message.reply_html(rf"Привет {user.mention_html()}! Попробуйте еще раз")
            return
    user_db = db_sess.query(User).filter(User.user_id == update.effective_message.chat_id).first()
    if user_db.is_admin:
        await update.message.reply_html(
            rf"Привет {user.mention_html()}! О чем сегодня поболтаем? Доступные команды: /choose - выбор формата ответа бота, /ban user_id, /unban user_id - блокировка и разблокировка юзера по тг id"
        )
    else:
        await update.message.reply_html(
            rf"Привет {user.mention_html()}! О чем сегодня поболтаем? Доступные команды: /choose - выбор формата ответа бота"
        )


# выбор варинта ответа бота
async def choose(update, context):
    reply_keyboard = [['/voice', '/text']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_html(rf"Выбери то как ты хочешь, чтобы я отвечал:", reply_markup=markup)


# если выбран текстовый ответ. Запись ответа юзера в бд
async def ans_text(update, context):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == update.effective_message.chat_id).first()
    user.model = 'text'
    db_sess.commit()
    db_sess.close()
    await update.message.reply_html(rf"Выбран ответ текстом", reply_markup=ReplyKeyboardRemove())


# если выбран голосовой ответ. Запись ответа юзера в бд
async def ans_voice(update, context):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == update.effective_message.chat_id).first()
    user.model = 'voice'
    db_sess.commit()
    db_sess.close()
    await update.message.reply_html(rf"Выбран ответ голосом", reply_markup=ReplyKeyboardRemove())


# сохранение истории чата в бд
def save_mem(user_id, text):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == user_id).first()
    user.story += text + ' || '
    if user.story.count("||") >= 5:
        save_memory(user.user_id, user.story)
    else:
        db_sess.commit()
        db_sess.close()


# генерирование текстового ответа
async def text_answer(chat_id, text_inp):
    text = GetResponse(text_inp, chat_id)
    save_mem(chat_id, f"{text}")
    return text


# генерирование голосового ответа
async def voice_answer(chat_id, text_inp):
    text = GetResponse(text_inp, chat_id)
    save_mem(chat_id, f"{text_inp}")
    res = synthesize(text=text, chat_id=chat_id, export_path=f'voice/{time.time()}.ogg')
    return res[0]


# обработчик сообщений
async def messages_handler(update, context):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == update.effective_message.chat_id).first()
    if not user.banned:
        if user.model == 'text':
            ans = await text_answer(update.effective_message.chat_id, update.message.text)
            await update.message.reply_text(f'{ans}')
        else:
            ans = await voice_answer(update.effective_message.chat_id, update.message.text)
            await update.message.reply_voice(ans)
    else:
        await update.message.reply_html(rf"Вы заблокированы администратором(((")


# выдача прав администратора
async def make_admin(update, context):
    db_sess = db_session.create_session()
    user = update.effective_user
    user_db = db_sess.query(User).filter(User.user_id == update.effective_message.chat_id).first()
    if user_db.is_admin:
        await update.message.reply_html(rf"Пользователь {user.mention_html()} уже является администратором")
    else:
        pas = update.message.text.split()[-1]
        if pas == 'admin_pas':
            user_db.is_admin = True
            await update.message.reply_html(rf"Пользователь {user.mention_html()} становится администратором")
            db_sess.commit()
            db_sess.close()
        else:
            await update.message.reply_text(rf"неверный пароль")


async def ban(update, context):
    db_sess = db_session.create_session()
    id_to_ban = update.message.text.split()[-1]
    user = db_sess.query(User).filter(User.user_id == id_to_ban).first()
    user_request = db_sess.query(User).filter(User.user_id == update.effective_message.chat_id).first()
    if user_request.is_admin:
        if user is None:
            await update.message.reply_html(rf"Пользователя с id={id_to_ban} не найдено")
        else:
            user.banned = True
            await update.message.reply_html(rf"Пользователь {user.mention_html()} заблокирован")
            db_sess.commit()
            db_sess.close()
    else:
        await update.message.reply_html(rf"недостаточно прав")


async def unban(update, context):
    db_sess = db_session.create_session()
    id_to_ban = update.message.text.split()[-1]
    user = db_sess.query(User).filter(User.user_id == id_to_ban).first()
    user_request = db_sess.query(User).filter(User.user_id == update.effective_message.chat_id).first()
    if user_request.is_admin:
        if user is None:
            await update.message.reply_html(rf"Пользователя с id={id_to_ban} не найдено")
        else:
            user.banned = True
            await update.message.reply_html(rf"Пользователь {user.mention_html()} заблокирован")
            db_sess.commit()
            db_sess.close()
    else:
        await update.message.reply_html(rf"недостаточно прав")


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("choose", choose))
    application.add_handler(CommandHandler("voice", ans_voice))
    application.add_handler(CommandHandler("text", ans_text))
    application.add_handler(CommandHandler('make_admin', make_admin))
    application.add_handler(CommandHandler('ban', ban))
    application.add_handler(CommandHandler('unban', unban))
    message_handler = MessageHandler(filters.TEXT, messages_handler)
    application.add_handler(message_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
