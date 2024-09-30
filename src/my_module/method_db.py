import sqlite3
from sqlite3 import Cursor, Connection
from typing import List, Tuple
import os

# Создание базы данных если её нет
def created_db() -> None:
    if not os.path.isdir("../data/database/user.db"):
        conn = sqlite3.connect("../data/database/user.db")
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id int, chat_id int, mailing boolean)""")
        conn.commit()
        cur.close()
        conn.close()


# Открытие БД
def open_db() -> [Connection, Cursor]:
    conn_local = sqlite3.connect('../data/database/user.db')
    cur_local = conn_local.cursor()
    return conn_local, cur_local


# Закрытие БД
def close_db(conn_local: Connection, cur_local: Cursor) -> None:
    cur_local.close()
    conn_local.close()


# Добавления пользователя в БД, если его нет
def add_user(message) -> None:
    conn, cur = open_db()
    cur.execute(f"""SELECT * FROM user WHERE user_id = {message.from_user.id}""")
    user = cur.fetchall()

    # Если пользователь с таким user_id отсутствует -> создаем нового пользователя в БД
    if not user:
        cur.execute("""INSERT INTO user (id, user_id, chat_id, mailing) VALUES (NULL, '%s', '%s', '%r')""" % (message.from_user.id, message.chat.id, False))
        conn.commit()

    close_db(conn, cur)


# Добавляем рассылку пользователю
def add_mailing(id_user: int) -> None:
    conn, cur = open_db()
    sql_update_query = f"""UPDATE user SET mailing = {True} WHERE user_id = {id_user}"""
    cur.execute(sql_update_query)
    conn.commit()
    close_db(conn, cur)


# Удаляем рассылку пользователю
def delete_mailing(id_user: int) -> None:
    conn, cur = open_db()
    sql_update_query = f"""UPDATE user SET mailing = {False} WHERE user_id = {id_user}"""
    cur.execute(sql_update_query)
    conn.commit()
    close_db(conn, cur)


# Получаем список всех пользователей с подпиской на рассылку
def get_mailing_user_all() -> List[Tuple[int]]:
    conn, cur = open_db()
    cur.execute("SELECT chat_id FROM user WHERE mailing = 1")
    user = cur.fetchall()
    return user


def get_profile(user_id: int) -> List[Tuple[int]]:
    conn, cur = open_db()
    cur.execute(f"""SELECT * FROM user WHERE user_id = {user_id}""")
    user = cur.fetchall()
    return user