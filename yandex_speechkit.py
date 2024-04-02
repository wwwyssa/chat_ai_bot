from argparse import ArgumentParser

from speechkit import model_repository, configure_credentials, creds

# Аутентификация через API-ключ.
configure_credentials(
    yandex_credentials=creds.YandexCredentials(
        api_key='AQVN2EdUhhPLh-zBnEkAI2PHiO4Crmygba-pafTx'
    )
)


def synthesize(text, export_path, voice='alexander', role='good'):
    model = model_repository.synthesis_model()

    model.voice = voice
    model.role = role
    result = model.synthesize(text, raw_format=False)
    result.export(export_path, 'ogg')


if __name__ == '__main__':
    voice = ['ermil']
    role = ['good']
    synthesize('Привет, как дела?', 'voice/res.ogg')
