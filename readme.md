# Chat ai tg bot

Данный бот создан для общения с несуществующей личностью. Если поговорить не с кем, то есть какой-никакой выход (данный
бот).

# To run:

В файл cfg.ini вставте API ключи OpenAI и YandexSpeechKIT, а так же токен Вашего телеграм бота.

```cmd
pip install -r requirements.txt
mkdir voice
python bot.py
```
Для запуска с РФ нужен VPN


### Что и зачем
bot.py - непосредственно тело бота;

chat_gpt.py - здесь все функции, которые непосредственно используют OpenAI API;

yandex_speechkit.py - здесь все функции, которые непосредственно используют YandexSpeechKIT API;