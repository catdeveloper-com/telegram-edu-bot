#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

# ======================================================================================================================
#   Copyright (c) 2022.
#   Сайт: https://catdeveloper.com
#   Разработчик: https://catdeveloper.com/kontakty
# ======================================================================================================================

"""Файл конфигурации."""

import os
from dotenv import load_dotenv

ABS_PATH = os.path.dirname(os.path.abspath(__file__))

load_dotenv()

MYSQL_DATABASE_NAME = os.environ.get('MYSQL_DATABASE_NAME', 'telegram_edu_bot')
MYSQL_DATABASE_USER = os.environ.get('MYSQL_DATABASE_USER', 'root')
MYSQL_DATABASE_PASSWORD = os.environ.get('MYSQL_DATABASE_PASSWORD', '')
MYSQL_DATABASE_HOST = os.environ.get('MYSQL_DATABASE_HOST', '127.0.0.1')
MYSQL_DATABASE_PORT = int(os.environ.get('MYSQL_DATABASE_PORT', 3306))

MONGO_DATABASE_NAME = os.environ.get('MONGO_DATABASE_NAME', 'telegram_edu_bot')
MONGO_DATABASE_USER = os.environ.get('MONGO_DATABASE_NAME', 'admin')
MONGO_DATABASE_PASSWORD = os.environ.get('MONGO_DATABASE_PASSWORD', '123')
MONGO_DATABASE_HOST = os.environ.get('MONGO_DATABASE_HOST', '127.0.0.1')
MONGO_DATABASE_PORT = int(os.environ.get('MONGO_DATABASE_PORT', 5432))
MONGO_DATABASE_URI = os.environ.get('MONGO_DATABASE_URI',
                                    f'mongodb://{MONGO_DATABASE_USER}:{MONGO_DATABASE_PASSWORD}@{MONGO_DATABASE_HOST}:'
                                    f'{MONGO_DATABASE_PORT}/{MONGO_DATABASE_NAME}')

TIMEZONE = os.environ.get('TIMEZONE', 'Europe/Moscow')

WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')
WEBHOOK_PORT = os.environ.get('WEBHOOK_PORT', 8443)
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', f'https://{WEBHOOK_HOST}:{WEBHOOK_PORT}')

API_TOKEN = os.environ.get('API_TOKEN')
MAX_MESSAGE_LEN = int(os.environ.get('MAX_MESSAGE_LEN', 4096))

OWNER_ID = os.environ.get('OWNER_ID')
ADMIN_GROUP_ID = os.environ.get('ADMIN_GROUP_ID')
SUPPORT_GROUP_ID = os.environ.get('SUPPORT_GROUP_ID')

SUPPORT_FILES_LIMIT = int(os.environ.get('SUPPORT_FILES_LIMIT', 3))
LECTURER_SPAM_FILES_LIMIT = int(os.environ.get('LECTURER_SPAM_FILES_LIMIT', 11))
SCHEDULE_CHANGES_FILE_LIMIT = int(os.environ.get('SCHEDULE_CHANGES_FILE_LIMIT', 11))

BAN_MESSAGE = os.environ.get('BAN_MESSAGE', '❌Ваш аккаунт заблокирован администратором❌')
NO_ACCESS_MESSAGE = os.environ.get('NO_ACCESS_MESSAGE', '❌Нет доступа к команде❌')
NO_OBJECT_ACCESS_MESSAGE = os.environ.get('NO_OBJECT_ACCESS_MESSAGE', 'Вы не можете использовать данный объект')
NO_ACCESS_FOR_LECTURERS_MESSAGE = os.environ.get('NO_ACCESS_FOR_LECTURERS_MESSAGE',
                                                 '⚠️Данная команда не предназначена для преподавателей, '
                                                 'команды доступные преподавателям находятся здесь: /home⚠️')
NO_PROCESS_FOR_CANCEL_MESSAGE = os.environ.get('NO_PROCESS_FOR_CANCEL_MESSAGE', 'Нет активных процессов для отмены')
PROCESS_CANCELED_BY_USER_MESSAGE = os.environ.get('PROCESS_CANCELED_BY_USER_MESSAGE',
                                                  'Процесс отменён по запросу пользователя')
UNLOCKED_MESSAGE = os.environ.get('UNLOCKED_MESSAGE', 'Вы снова можете пользоваться ботом')
TOO_MANY_REQUESTS_MESSAGE = os.environ.get('TOO_MANY_REQUESTS_MESSAGE', 'Слишком много запросов!')

FOR_ONLY_REGISTERED_USERS_MESSAGE = os.environ.get('FOR_ONLY_REGISTERED_USERS_MESSAGE',
                                                   '/register - регистрация для студентов\n/register_as_lecturer - '
                                                   'регистрация для преподавателей')
TERMS_AGREE_PHRASE = os.environ.get('TERMS_AGREE_PHRASE', 'я принимаю условия пользования')

BOT_VERSION = os.environ.get('BOT_VERSION', 'я принимаю условия пользования')
DEVELOPER_CONTACTS = os.environ.get('DEVELOPER_CONTACTS', 'https://catdeveloper.com/kontakty')

LINE_BREAK_SYMBOL = os.environ.get('LINE_BREAK_SYMBOL', '/n')

TEXT_DOMAIN = os.environ.get('TEXTDOMAIN', 'telegram_edu_bot')

STICKERS = {
    'cat 0_-': 'CAACAgIAAxkBAAEEHudiK91hAgxXrPoLnp3zh6GJVN-jngACKxUAAulAsEgBTshi2Qsv3SME',
    'cat -_____-': 'CAACAgIAAxkBAAEEHuliK98jej8b0OnQ3QS3zd337jqUIwACAhMAAlBJsUgd9H9aUsUKoyME',
    'cat 0_0': 'CAACAgIAAxkBAAEEHvFiK-1iUYuTI6ZqNF6ZPlbpYHHMLwAC3xcAAqCRsEi20oX3s2HlxiME',
    'cat 0w0': 'CAACAgIAAxkBAAEEHu9iK-1CDtmwOPg-WcH6DUx61HIbBwACohYAAqyQsUjHeAJWEuItuSME',
    'cat ^w^': 'CAACAgIAAxkBAAEELFliMU-HS6avsyMejVwrJ7LqmD2zkgACyBcAAivusEi_nbHho1cfWCME',
    'cat run': 'CAACAgIAAxkBAAEEHvxiLAX4LPuDPgO8ATihnNS76xUOWwACgBIAAujW4hJpBWx11v6IkyME',
    'programmer coding ok': 'CAACAgIAAxkBAAEEHvdiLAABXOvJjMJ3t84MDgztP8xDiGgAAiCvAQABY4tGDBpWi03b9YciIwQ',
    'admin_warn': 'CAACAgIAAxkBAAEEHwABYiwGv0pP__ypjxVeb0iqto53NOQAAtUAAz818gRemiywlz5eSiME',
    'admin_ban': 'CAACAgIAAxkBAAEEHv5iLAaiUmlc4WBSAuvTKU5FClPvzwAC1gADPzXyBIvhodyCVNfRIwQ',
}

DAYS_START_PHRASES = ['В понедельник', 'Во вторник', 'В среду', 'В четверг', 'В пятницу', 'В субботу', 'В Воскресенье']
TEXT_NUMBERS_NAMES = ["Нулевой", "Первой", "Второй", "Третьей", "Четвёртой", "Пятой"]
EMOJI_NUMBERS = {"0": "0️⃣", "1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣"}
DAYS_NAMES = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

ALLOW_ACCESS_MODES = {'white_list': "Бот доступен только после прохождения регистрации",
                      'strict_access': "Бот доступен только тем, кто уже зарегестрирован, "
                                       "остальные не могу регестрироваться",
                      'debug': "Режим для проведения технических работ, бот доступен только админимтраторам,"
                               " остальным выведется уведомление о том, что бот на техническом обслуживании"}

ALL_MESSAGES_PREFIX = f"{BOT_VERSION}\n\n"

T_WARN = "Предупреждаем, что вы запросили расписание на <u><b>завтра</b></u>, <u><b>но сейчас уже идёт " \
         "новый день</b></u>, и расписание будет отображено относительно <u><b>текущего дня</b></u>," \
         " <u><b>а не вчерашнего</b></u>!"
T_GOOD_MORNING_MESSAGE_WARNING = f"🤗 Доброе утро! {T_WARN}"
T_GOOD_NIGHT_MESSAGE_WARNING = f"😴 Доброй ночи! {T_WARN}"

N_WARN = "Предупреждаем, что вы запросили расписание на <u><b>сегодня</b></u>, <u><b>но сейчас уже идёт " \
         "новый день</b></u>, по этому будет отображено расписание на <u><b>новый (текущий) день</b></u>," \
         " <u><b>а не вчерашний</b></u>!"
N_GOOD_MORNING_MESSAGE_WARNING = f"🤗 Доброе утро! {N_WARN}"
N_GOOD_NIGHT_MESSAGE_WARNING = f"😴 Доброй ночи! {N_WARN}"

