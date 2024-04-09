
from telebot import TeleBot,types
from telebot.types import ReplyKeyboardMarkup
from config import *
from gpt import (
    count_tokens,
    create_prompt,
    create_additional,
    ask_gpt
)
import sqlite3
import logging
from datetime import datetime
from database import (
    create_db,
    create_table,
    get_dialog_for_user,
    add_record_to_table,
    get_value_from_table,
    is_value_in_table,
    get_users_amount
)
from story import genres,characters,settings

logging.basicConfig(filename='bot.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#Создаем бота
bot = TeleBot(BOT_TOKEN)
MAX_LETTERS = MAX_MODEL_TOKENS

# Словарь для хранения настроек пользователя
user_data = {}
collection = []

# Функция для создания клавиатуры с нужными кнопочками

def create_keyboard(buttons_list):

    logging.debug(f"the bot has created buttons")
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

# Приветственное сообщение /start

@bot.message_handler(commands=['start'])
def start(message):
    global user_data
    global collection
    logging.debug(f"User {message.from_user.id} started the bot")
    create_db()
    create_table()
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    bot.send_message(user_id,
                     text=f"Привет, {user_name}! Я бот, который создает истории с помощью нейросети.\n"
                          f"Мы будем писать истории поочередно. Я начну, а ты продолжишь.\n"
                          "Напиши /new_story, чтобы начать новую историю.\n"
                          f"А когда ты закончишь, напиши /end.",
                     reply_markup=create_keyboard(["/new_story"]))
    user_data[user_id] = {'genre': '', 'character': '', 'setting': '', 'additional_info': ''}
    collection = []

# Команда /begin

@bot.message_handler(commands=['begin'])
def begin_story(message):
    logging.debug(f"User {message.from_user.id} use begin")
    user_id = message.from_user.id
    # Проверяем, что пользователь прошел регистрацию
    # Запрашиваем ответ нейросети
    if user_id not in user_data:
        bot.send_message(user_id,text="Введи /start, чтобы начать пользоваться ботом")
    get_story(message)

# Команда /end
@bot.message_handler(commands=['end'])
def end_func(message):
    #global collection
    global user_data
    global session_id
    user_id = message.from_user.id
    logging.debug(f"User {message.from_user.id} use end")
    if  user_data[user_id]['genre'] == "" and user_data[user_id]['character'] == "" and user_data[user_id]['setting'] == "":
        bot.send_message(message.chat.id, text=f"Сначала нужно начать новую историю /new_story", reply_markup=create_keyboard(["/new_story"]))
    else:
        bot.send_message(message.chat.id, text=f"Генерирую конец истории...")
        user_data[user_id]['additional_info']="end"
        collection: list = get_dialog_for_user(user_id, session_id)
        gpt_text= ask_gpt(collection,'end')
        bot.send_message(message.chat.id, text=f"Бот-сценарист:\n"
                                           f"{gpt_text}", reply_markup=create_keyboard(["/new_story"]))
        add_record_to_table(
          user_id,
          "assistant",
          gpt_text,
          datetime.now(),
          count_tokens(gpt_text),
          session_id
        )
        user_data[user_id] = {'genre': '', 'character': '', 'setting': '', 'additional_info': ''}
# Команда /new_story

@bot.message_handler(commands=['new_story'])
def registration(message):
    global user_data
    global collection
    global session_id
    user_id=message.from_user.id
    logging.debug(f"User {message.from_user.id} use new_story")
    session_id = 1
    if is_value_in_table(DB_TABLE_PROMPTS_NAME, column_name= 'user_id',value=user_id) == True:
        session_id = get_value_from_table('session_id', user_id) + 1
    user_data[user_id] = {'genre': '', 'character': '', 'setting': '', 'additional_info': ''}
    collection=[]
    user_count = get_users_amount(DB_TABLE_PROMPTS_NAME)
    if user_count>=MAX_USERS:
        bot.send_message(message.chat.id,
                     text="Превышено количество пользователей. Попробуй позже")
    # Проверяем, что пользователь прошел регистрацию
    # Запрашиваем ответ нейросети
    else:
        bot.send_message(message.chat.id,
                         text="Для начала выбери жанр своей истории из предложенных или просто напиши:\n",
                         reply_markup=create_keyboard(genres))
        bot.register_next_step_handler(message, handle_genre)

def handle_genre(message):
    global user_data
    """Записывает ответ на вопрос о жанре в БД и отправляет следующий вопрос о персонаже"""
    user_id = message.from_user.id
    #считывает ответ на предыдущий вопрос
    genre = message.text
    user_data[user_id]['genre'] = genre

    #отправляет следующий вопрос
    bot.send_message(message.chat.id,
                     text= "Выбери главного героя из предложенных или просто напиши:",
                     reply_markup=create_keyboard(characters))
    bot.register_next_step_handler(message, handle_character)

def handle_character(message):
    global user_data
    """Записывает ответ на вопрос о персонаже в БД и отправляет следующий вопрос о сеттинге"""
    user_id = message.from_user.id
    #считывает ответ на предыдущий вопрос
    character = message.text
    user_data[user_id]['character'] = character
    #Если пользователь отвечает что-то не то, то отправляет ему вопрос ещё раз
    #settings_string = "\n".join([f"{name}: {description}" for name, description in settings.items*()])
    #отправляет следующий вопрос
    bot.send_message(message.chat.id, "Выбери сеттинг из предложенных или просто напиши:",
    #                                  "\n"+ settings_string,
                     reply_markup=create_keyboard(settings))
    bot.register_next_step_handler(message, handle_setting)

def handle_setting(message):
    global user_data
    """Записывает ответ на вопрос о сеттинге в БД и отправляет следующий вопрос о дополнительной информации"""
    user_id = message.from_user.id
    #считывает ответ на предыдущий вопрос
    setting = message.text
    user_data[user_id]['setting'] = setting
    #отправляет следующий вопрос
    bot.send_message(message.chat.id, text="Если ты хочешь, чтобы мы учли ещё какую-то информацию, "
                                           "напиши её сейчас. Или ты можешь сразу переходить "
                                           "к истории написав /begin.",
                     reply_markup=create_keyboard(["/begin"]))
    bot.register_next_step_handler(message, handle_add_info)

def handle_add_info(message):
    global user_data
    """Записывает ответ на вопрос о дополнительной информации в БД"""
    user_id = message.from_user.id
    #считывает предыдущее действие
    additional_info = message.text
    if additional_info == "/begin":
        begin_story(message)
    else:
        #обновляем данные о пользователе в БД
        user_data[user_id]['additional_info'] = additional_info
        #отправляет следующий вопрос
        bot.send_message(message.chat.id, text="Спасибо! Всё учтём :)\n "
                                           "Напиши /begin, чтобы начать писать историю. ",
                     reply_markup=create_keyboard(["/begin"]))



# Обработчик вопросов

@bot.message_handler(content_types=['text'])

def get_story(message: types.Message):
    #global collection
    global session_id
    global user_data
    user_id = int(message.from_user.id)



    continue_story = message.text
    if  user_data[user_id]['genre'] == "" and user_data[user_id]['character'] == "" and user_data[user_id]['setting'] == "":
        bot.send_message(message.chat.id, text=f"Сначала нужно начать новую историю /new_story", reply_markup=create_keyboard(["/new_story"]))
    else:
        if continue_story == "" or continue_story == "/begin":
            system_story = create_prompt(user_data, message.from_user.id)
            #collection.append({'role': 'system', 'content': system_story})
            add_record_to_table(
            user_id,
            "system",
            system_story,
            datetime.now(),
            count_tokens(system_story),
            session_id
            )



        user_data[user_id]['additional_info'] = continue_story
        user_story = create_additional(user_data, user_id)
        #collection.append({'role': 'user', 'content': user_story})
        add_record_to_table(
          user_id,
          "user",
          user_story,
          datetime.now(),
          count_tokens(user_story),
          session_id
        )

        collection: list = get_dialog_for_user(user_id, session_id)
        #Проверка количества токенов за сессию
        if count_tokens(collection) >= MAX_TOKENS_IN_SESSION:
            bot.send_message(message.chat.id, text="Превышено максимальное количество запросов за сессию", reply_markup=create_keyboard(["/new_story"]))
        else:
            bot.send_message(message.chat.id, text=f"Генерирую...", reply_markup=create_keyboard(["/end"]))
            gpt_text= ask_gpt(collection)
            #collection.append({'role': 'assistant', 'content': gpt_text})
            bot.send_message(message.chat.id, text=f"Бот-сценарист:\n"
                                           f"{gpt_text}.\n"
                                           f"\n"
                                           f" Можешь написать продолжение истории или нажать кнопку /end")
            add_record_to_table(
            user_id,
            "assistant",
            gpt_text,
            datetime.now(),
            count_tokens(gpt_text),
            session_id
            )





# Команда /help

@bot.message_handler(commands=['help'])
def support(message):
    logging.debug(f"User {message.from_user.id} use help")
    bot.send_message(message.from_user.id,
                     text="Чтобы приступить к решению задачи: Выбери предмет и уровень сложности ответов, а затем напиши условие задачи"
                     )



### Debug: вызов отладочного файла
@bot.message_handler(commands=["debug"])
def debug(message):
    logging.debug(f"bot send log file")
    bot.send_document(message.chat.id, open(r'C:\Users\artem\PycharmProjects\pythonProject\bot.log', 'rb'))
bot.polling()


