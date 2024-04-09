LOGS_PATH = 'logs.txt'
DB_DIR = 'db'
DB_NAME = 'gpt_help.db'
DB_TABLE_PROMPTS_NAME = 'prompt'
ADMIN_ID = ''
TOKEN = 't1.9euelZqQlpmRmZ6clsiSj86LjY6Kj-3rnpWam56Jj5OVyZXMiYrKno6WlpHl9PdzAypP-e92FRag3fT3MzInT_nvdhUWoM3n9euelZqQyYqSx5CVjcvGlo2XjZ6Vz-_8xeuelZqQyYqSx5CVjcvGlo2XjZ6Vz73rnpWakprLlp6cy5WXzZXPm4yLj8y13oac0ZyQko-Ki5rRi5nSnJCSj4qLmtKSmouem56LntKMng.OetpWZlxTw9SQf5LxCqT8dOC3O8tFIacotzCkH1ypZCHaKouRqaefUv3MeostyqNpTEYRnSY7gFZY0oDVmQGCQ'
FOLDER_ID = 'b1g9hi632eqnkei53ehp'
BOT_TOKEN='6917414946:AAG5f4pffHsvNy84rDg0TcIWbGaOOC5ZRkE'
#Максимальное количество пользователей бота
MAX_USERS = 3
#Модель GPT
GPT_MODEL = 'yandexgpt-lite'
#Ограничение на выход модели в токенах
MAX_MODEL_TOKENS = 1000
#Креативность GPT (от 0 до 1)
MODEL_TEMPERATURE = 0.6
#Каждому пользователю выдаем 1000 токенов на 1 сеанс общения
MAX_TOKENS_IN_SESSION = 1000
SYSTEM_PROMPT=(
    "Ты пишешь историю вместе с человеком. "
    "Историю вы пишите по очереди. Начинает человек, а ты продолжаешь. "
    "Если это уместно, ты можешь добавлять диалог между персонажами. "
    "Диалоги пиши с новой строки и отделяй тире. "
    "Не пиши никакого пояснительного текста в начале, а просто логично продолжай историю."
)
CONTINUE_STORY = 'Продолжи сюжет в 1-3 предложения и оставь интригу. Не пиши никакой пояснительный текст от себя'
END_STORY = 'Напиши завершение истории c неожиданной развязкой. Не пиши никакой пояснительный текст от себя'
