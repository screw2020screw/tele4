import logging
import json
import requests
import time
import os
from transformers import AutoTokenizer

from config import *
from database import get_dialog_for_user


TOKEN_PATH = 'gpt_token.json'
FOLDER_ID_PATH = 'gpt_folder_id.txt'

logging.basicConfig(filename='bot.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def create_prompt(user_data, user_id):
        prompt=SYSTEM_PROMPT
        prompt+=(f" Напиши начало истории в стиле {user_data[user_id]['genre']}"
                 f" с главным героем {user_data[user_id]['character']}"
                 f". Вот начальный сеттинг: {user_data[user_id]['setting']}"
                 ". Начало должно быть коротким, 1-3 предложения.")
        prompt += '. Не пиши никакие подсказки пользователю, что делать дальше. Он сам знает.'
        return prompt

def create_additional(user_data, user_id):

    if user_data[user_id]['additional_info'] != "/begin":
        additional = f"{user_data[user_id]['additional_info']}"
    else:
        additional = "begin"
    return additional

def create_new_token():
    """Создание нового токена"""
    os.system(f'yc iam create-token --format json > {TOKEN_PATH}')

def creds():
    try:
        with open(TOKEN_PATH, 'r')as f:
            d = json.load(f)
            expritation = d['expires_at']
        if expritation < time.time():
            create_new_token()
    except:
        create_new_token()

    with open(TOKEN_PATH, 'r') as f:
        d = json.load(f)
        token=d['access_token']

    with open(FOLDER_ID_PATH, 'r') as f:
        folder_id=f.read().strip()

    return token, folder_id

def ask_gpt(collection, mode='continue'):
    """Запрос к Yandex GPT"""

    #Получаем токен и folder_id, так как время жизни токена 12 часов
    token = TOKEN
    folder_id = FOLDER_ID

    url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{folder_id}/{GPT_MODEL}/latest",
        "completionOptions": {
            "stream": False,
            "temperature": MODEL_TEMPERATURE,
            "maxTokens": 100
        },
        "messages": []
    }
    for row in collection:
        content = row['content']

        # Добавь дополнительный текст к сообщению пользователя в зависимости от режима
        if mode == 'continue' and row['role'] == 'user':
            content+=" " + CONTINUE_STORY
            pass
        elif mode == 'end' and row['role'] == 'user':
            content+=" " + END_STORY
            pass

        data["messages"].append(
                {
                    "role": row["role"],
                    "text": content
                }
            )

    result_for_test_mode = 'Empty message for test mode'
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            logging.debug(f"Response {response.json()} Status code: {response.status_code} Message {response.text}")
            result = f"Status code {response.status_code}. Подробности см. в журнале."
            return result
        result = response.json()['result']['alternatives'][0]['message']['text']
    except Exception as e:
        #logging.ERROR(f"An unexpected error occured: {e}")
        result = "Произошла непредвиденная ошибка. Подробности см. в журнале."

    return result

if __name__ == "__main__":
    pass



# Подсчитывает количество токенов в тексте
def count_tokens(message):
    my_string = " ".join(str(element) for element in message)
    headers = { # заголовок запроса, в котором передаем IAM-токен
        'Authorization': f'Bearer {TOKEN}', # token - наш IAM-токен
        'Content-Type': 'application/json'
    }
    data = {
       "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest", # указываем folder_id
       "maxTokens": MAX_MODEL_TOKENS,
       "text": my_string # text - тот текст, в котором мы хотим посчитать токены
    }
    return len(
        requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
            json=data,
            headers=headers
        ).json()['tokens']
    ) # здесь, после выполнения запроса, функция возвращает количество токенов в text


"""collection: list = get_dialog_for_user(5795332738, 1)
print(get_dialog_for_user(5795332738, 1))
print(count_tokens(collection))"""
