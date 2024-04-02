from openai import OpenAI
import os
import configparser

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


# Функция для получения ответа OpenAI
def GetResponse(text):
    completion = client.chat.completions.create(
        model=model,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"Ты общаешься с пользователем описание которого представлено ниже:"},
            {"role": "user", "content": text}
        ]
    )
    return completion.choices[0].message.content


print(GetResponse('Привет, как дела?'))
