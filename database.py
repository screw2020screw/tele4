import sqlite3
import logging
from config import *
import datetime
logging.basicConfig(filename='bot.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Создание базы данных GPT_help.db
def create_db():
    con = sqlite3.connect(DB_NAME)
    con.close()

# Создание таблицы prompt если её нет
def create_table():
    logging.debug(f"User create table")
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    query='''
    CREATE TABLE IF NOT EXISTS prompt (
    id INTEGER PRIMARY KEY,
    user_id INTEGER, 
    role TEXT, 
    content TEXT,
    date DATETIME,
    tokens INTEGER, 
    session_id INTEGER);
    '''
    cur.execute(query)
    con.close()

#Функция для вывода всей таблицы (для проверки)
#Создает запрос SELECT *FROM имя_таблицы
def get_all_rows(table_name):
    rows = execute_selection_query(f'SELECT * FROM {table_name} ORDER BY date desc')
    for row in rows:
        print(row)


#Функция для вывода количества пользователей за последний час (для проверки)
def get_users_amount(table_name):
    td_object = datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=1, weeks=0)
    date_session_start = datetime.datetime.now()-td_object
    date_session_stop = datetime.datetime.now()
    sql_query = f"SELECT COUNT (DISTINCT user_id) AS unique_user FROM {table_name} WHERE date BETWEEN '{date_session_start}' AND '{date_session_stop}'"
    rows=execute_selection_query(sql_query)
    for row in rows:
       unique_user = int(row[0])
    return unique_user


#Функция для добавления пользователя в таблицу
def add_user(self, id, story=''):
    if not self.id_in_table(id):
        self._insert_row(self, DB_NAME, [id, story])
    else:
        print(f"Ошибка при добавлении: пользователя с id = {id} уже есть в таблице")

#Функция для удаления всех записей из таблицы
#Создает запрос DELETE FROM имя_таблицы
def clean_table(table_name):
    execute_query(f'DELETE FROM {table_name}')

#Функция для вставки новой строки в таблицу
#Принимает список значений для каждой колонки и название колонки
#Создает запрос INSERT INTO имя_таблицы (колонка1, колонка2) VALUES (?,?)[значение1, значение2]
def insert_row(table_name, values, columns=''):
    if columns!='':
        columns = '(' + ', '.join(columns) + ')'
    sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({', '.join(['?'] * len(values))})"
    execute_query(sql_query)

#Функция для проверки, есть ли элемент в указанном столбце таблицы
def is_value_in_table(table_name, column_name, value):
    sql_query = f"SELECT {column_name} FROM {table_name} WHERE {column_name} = {value} order by date desc"
    rows=execute_selection_query(sql_query)
    if rows != []:
        proverka = True
    else:
        proverka = False
    return proverka

#Функция, записывающая историю запросов в таблицу
def add_record_to_table(user_id, role, content, date, tokens, session_id):
    sql_query = f"INSERT INTO {DB_TABLE_PROMPTS_NAME} (user_id, role, content, date, tokens, session_id) VALUES ('{user_id}', '{role}', '{content}', '{date}', '{tokens}', '{session_id}')"
    execute_query(sql_query)

#Функция для получения последнего значения из таблицы для пользователя
def get_value_from_table(value, user_id):
    sql_query=f'SELECT {value} FROM {DB_TABLE_PROMPTS_NAME} where user_id = {user_id} order by date'
    rows=execute_selection_query(sql_query)
    for row in rows:
       user_session = int(row[0])
    return user_session

#Функция для получения диалога для указанного пользователя
def get_dialog_for_user(user_id, session_id):
    # Выбираем значения нужных полей
    sql_query=(
        f'SELECT role,content FROM {DB_TABLE_PROMPTS_NAME} where user_id = {user_id} AND tokens IS NOT NULL AND session_id = {session_id} order by date asc'
    )
    rows  = execute_selection_query(sql_query)
    # Создаем словарик запроса для GPT
    user_collection = [{'role': col1, 'content': col2} for (col1, col2) in rows]
    return user_collection

#Общая функция запроса данных из таблицы
def execute_selection_query(sql_query):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    # Выбираем значения нужных полей
    cur.execute(sql_query)
    a = cur.fetchall()
    con.close()
    return a

#Общая функция изменения данных в таблице
def execute_query(sql_query):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute(sql_query)
    con.commit()
    con.close()




