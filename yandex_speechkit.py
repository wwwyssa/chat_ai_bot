from time import time_ns

from speechkit import model_repository, configure_credentials, creds

# Аутентификация через API-ключ.
configure_credentials(
    yandex_credentials=creds.YandexCredentials(
        api_key='AQVN2EdUhhPLh-zBnEkAI2PHiO4Crmygba-pafTx'
    )
)


def synthesize(text, chat_id, export_path, voice='alexander', role='good'):
    model = model_repository.synthesis_model()

    model.voice = voice
    model.role = role
    try:
        result = model.synthesize(text, raw_format=False)
    except Exception as e:
        print(e)
        return
    result.export(export_path, 'ogg')
    return export_path, chat_id


if __name__ == '__main__':
    voice = ['ermil']
    role = ['good']
    synthesize('Привет, как дела? ', chat_id='1', export_path=f'voice/{str(time_ns())}.ogg')
