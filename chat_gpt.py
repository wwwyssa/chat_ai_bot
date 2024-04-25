from openai import OpenAI
import os
import configparser

from data import db_session
from data.users import User

config = configparser.ConfigParser()
config.read('cfg.ini')

# Настройки OpenAI
api_key = config["GPT"]["api_key"]
model = config["GPT"]["model"]
frequency_penalty = float(config["GPT"]["frequency_penalty"])
presence_penalty = float(config["GPT"]["presence_penalty"])
temperature = float(config["GPT"]["temperature"])
max_tokens = int(config["GPT"]["max_tokens"])
client = OpenAI(api_key=api_key)
system_prompt = open('gpt_prompt.txt', 'r', encoding='utf-8').read()
sum_prompt = open('save_mem.txt', 'r', encoding='utf-8').read()  # Промпт для суммаризации диалога


# Функция для получения ответа OpenAI
def GetResponse(text, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == user_id).first()
    completion = client.chat.completions.create(
        model=model,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "system",
             "content": f"Ты общаешься с пользователем описание которого представлено ниже , при своих ответах учитывай описание пользователя:\n{user.story}"},
            {"role": "user", "content": text}
        ]
    )

    if completion.choices[0].message.content[-1].rstrip() not in '.!?':
        t_a = completion.choices[0].message.content[::-1]
        pos_v = 100000
        pos_q = 100000
        pos_d = 100000
        if '!' in t_a:
            pos_v = t_a.index('!')
        if '?' in t_a:
            pos_q = t_a.index('?')
        if '.' in t_a:
            pos_d = t_a.index('.')
        completion.choices[0].message.content = completion.choices[0].message.content[:-min(pos_d, pos_q, pos_v)]
    print(completion.choices[0].message.content)

    return completion.choices[0].message.content


#суммаризация истории сообщений
def save_memory(chat_id, conversation):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.chat_id == chat_id).first()

    completion = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": sum_prompt},
            {"role": "user", "content": f"{user.story}\n{conversation}"}
        ]
    )
    try:
        user.story = completion.choices[0].message.content
        db_sess.commit()
    except:
        print(f"Ошибка сохранения памяти для пользователя - {user.user_id}")
        db_sess.rollback()
    db_sess.close()
