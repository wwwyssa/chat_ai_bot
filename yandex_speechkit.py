import configparser

from speechkit import model_repository, configure_credentials, creds

config = configparser.ConfigParser()
config.read('cfg.ini')
api_key = config["YANDEX"]["api_key"]

configure_credentials(
    yandex_credentials=creds.YandexCredentials(
        api_key=api_key
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