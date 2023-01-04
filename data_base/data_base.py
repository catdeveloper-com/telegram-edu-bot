#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

# ======================================================================================================================
#   Copyright (c) 2022.
#   Сайт: https://catdeveloper.com
#   Разработчик: https://catdeveloper.com/kontakty
# ======================================================================================================================

"""Модуль для работы с базой данных."""

from __future__ import annotations

from typing import Union

import pymysql
from pymysql.cursors import Cursor

from config import MYSQL_DATABASE_USER, MYSQL_DATABASE_PASSWORD, MYSQL_DATABASE_NAME, MYSQL_DATABASE_PORT, \
    MYSQL_DATABASE_HOST, BOT_VERSION
from create_bot import gettext as _
from exceptions.bot_stop import UnhandledException
from loggers import errors_logger
from utils.functions import is_empty


class MYSQLDatabase:
    """Класс для работы с MYSQL базой данных."""

    async def _get_sql_connection(self) -> pymysql.Connection:
        """
        Возвращает объект подключения к БД MySQL.

        Returns:
            pymysql.Connection: объект соединения с базой данных MYSQL

        Raises:
            UnhandledException: не удалось подключиться к MYSQL базе данных
        """
        try:
            connection = pymysql.connect(
                host=MYSQL_DATABASE_HOST,
                port=MYSQL_DATABASE_PORT,
                database=MYSQL_DATABASE_NAME,
                user=MYSQL_DATABASE_USER,
                password=MYSQL_DATABASE_PASSWORD,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
                charset="utf8"
            )
            return connection
        except Exception as e:
            message = _('Ошибка при получении соединения с MYSQL: "%s"' % e)
            errors_logger.exception(message)
            raise UnhandledException(message)

    async def sql_transaction(self, sql_requests: list) -> list:
        """
        Выполняет транзакцию из поступивших SQL запросов.

        Args:
            sql_requests: список SQL запросов

        Returns:
            list: список строк, каждая строка - словарь вида {имя_столбца:значение}

        Raises:
            UnhandledException: необрабатываемое исключение во время SQL транзакции
        """
        try:
            connection = await self._get_sql_connection()
            with connection.cursor() as cursor:
                connection.begin()
                last_success_request = None
                for sql_request in sql_requests:
                    cursor.execute(sql_request)
                    last_success_request = sql_request
                connection.commit()
                connection.close()
                return [x for x in cursor.fetchall()]
        except Exception as e:
            message = _('Ошибка "%s" при выполнении запроса, последний удачный запрос: "%s"' % (e,
                                                                                                last_success_request))
            errors_logger.exception(message)
            raise UnhandledException(message)

    async def sql(self, sql_request: str) -> list:
        """
        Выполняет SQL запрос к MYSQL.

        Args:
            sql_request: SQL запрос

        Returns:
            list: список строк, каждая строка - словарь вида {имя_столбца:значение}

        Raises:
            UnhandledException: необрабатываемое исключение при выполнении sql запроса
        """
        try:
            connection = await self._get_sql_connection()
            with connection.cursor() as cursor:
                cursor.execute(sql_request)
                connection.commit()
                connection.close()
                return [x for x in cursor.fetchall()]  # [{k:v},{k:v}]]
        except Exception as e:
            message = _('Ошибка "%s" при выполнении sql запроса: "%s"' % (e, sql_request))
            errors_logger.exception(message)
            raise UnhandledException(message)

    async def get_bot_user_info_by_telegram_id(self, telegram_id: int) -> Union[dict, None]:
        """
        Получает всю информацию о пользователе по telegram id.

        Args:
            telegram_id: telegram id

        Returns:
            dict: Словарь со столбцами из таблицы bot_user
            None: если ничего не найдено
        """
        sql_request = f"SELECT * FROM `bot_user` WHERE `telegram_id`='{telegram_id}'"
        response = await self.sql(sql_request)
        if await is_empty(response): return None
        user = response[0]
        for item in user.keys():
            if type(user[item]) == str:
                user[item] = user[item].replace("'", "")
        return user

    async def telegram_username_to_telegram_id(self, telegram_username: str) -> Union[int, None]:
        """
        Преобразует telegram username в telegram id.

        Args:
            telegram_username: telegram_username

        Returns:
            int: telegram id
            None: ничего не найдено
        """
        if telegram_username.startswith("@"):
            telegram_username = telegram_username.replace("@", "")
        if await is_empty(telegram_username): return None

        sql_request = f"SELECT `telegram_id` FROM `bot_user` WHERE BINARY `telegram_username`='{telegram_username}'"
        response = await self.sql(sql_request)

        return None if await is_empty(response) else int(response[0]['telegram_id'])

    async def telegram_id_to_bot_user_id(self, telegram_id: int) -> Union[int, None]:
        """
        Возвращает id пользователя бота по telegram id.

        Args:
            telegram_id: telegram id

        Returns:
            int: список id пользователей бота
            None: если ничего не найдено
        """

        sql_request = f"SELECT `id` FROM `bot_user` WHERE `telegram_id` = '{telegram_id}'"
        response = await self.sql(sql_request)

        return None if await is_empty(response) else response[0]['id']

    async def students_group_name_to_id(self, students_group_name: str) -> Union[int, None]:
        """
        Возвращает id группы студентов по её названию.

        Args:
            students_group_name: список id групп

        Returns:
            int: id группы
            None: если ничего не найдено
        """
        sql_request = f"""SELECT `id` FROM `students_group` WHERE `name` = '{students_group_name}')"""
        response = await self.sql(sql_request)

        return None if await is_empty(response) else response[0]['id']

    async def get_telegram_ids_by_students_group(self, students_group: str) -> Union[list, None]:
        """
        Получает список telegram id студентов по переданной группе.

        Args:
            students_group: Имя группы

        Returns:
            list: список telegram id студентов
            None: ничего не найдено или группа не существует
        """
        group_exist = await self.check_students_group_in_db(students_group)
        if not group_exist: return None

        group_id = await self.students_group_name_to_id(students_group)
        if await is_empty(group_id): return None
        sql_request = f"SELECT `bot_user_id` FROM `bot_user_students_group` WHERE `students_group_id`='{group_id}'"
        response = await self.sql(sql_request)

        return None if await is_empty(response) else [x['bot_user_id'] for x in response]

    async def get_bot_settings(self) -> Union[dict, None]:
        """
        Получает настройки бота.

        Returns:
            dict: словарь настроек бота
            None: ничего не найдено
        """
        sql_request = f"SELECT * FROM `setting`"
        response = await self.sql(sql_request)
        settings = {}
        for item in response:
            settings.update({item['name']: item['value']})
        return None if await is_empty(response) else settings

    async def update_bot_settings(self, name: str, value: str) -> Union[bool, None]:
        """
        Обновляет значение переданного параметра.

        Args:
            name: имя параметра
            value: значение параметра

        Returns:
            bool: False - настройки не найдены
            None: метод выполнился

        Raises:
            UnhandledException: передан несуществующий параметр
        """
        settings = await self.get_bot_settings()
        if await is_empty(settings): return False

        if not name in settings.keys(): raise UnhandledException(
            _('"%s" - такой параметр не существует, по этому его нельзя обновить' % name))

        sql_request = f"UPDATE `setting` SET `value`='{value}' WHERE `name`='{name}'"
        await self.sql(sql_request)

        return None

    async def check_telegram_id_in_db(self, telegram_id: int) -> bool:
        """
        Проверяет наличие telegram id в базе данных MYSQL.

        Args:
            telegram_id: telegram id

        Returns:
            bool: True - telegram id есть в БД, False - telegram id нет в БД
        """
        sql_request = f"SELECT `telegram_id` FROM `bot_user` WHERE `telegram_id`='{telegram_id}'"
        response = await self.sql(sql_request)
        return False if await is_empty(response) else True

    async def check_bot_user_registration_by_telegram_id(self, telegram_id: int) -> Union[bool, None]:
        """
        Проверяет регистрацию пользователя по переданному telegram id.

        Args:
            telegram_id: telegram id

        Returns:
            bool: True - зарегистрирован, False - Не зарегистрирован
            None: не найден
        """
        sql_request = f"SELECT `is_registered` FROM `bot_user` WHERE `telegram_id`='{telegram_id}'"
        response = await self.sql(sql_request)
        if await is_empty(response): return None

        return True if response[0]['is_registered'] else False

    async def check_students_group_in_db(self, students_group: str) -> bool:
        """
        Проверяет наличие группы в базе данных.

        Args:
            students_group: название группы

        Returns:
            bool: True - есть, False - нет
        """
        sql_request = f"SELECT `id` FROM `students_group` WHERE `name`='{students_group}'"
        response = await self.sql(sql_request)
        return True if await is_empty(response) else False

    async def add_bot_user_in_db(self,
                                 telegram_id: int,
                                 telegram_username: str = None,
                                 first_name: str = 'нет_имени',
                                 last_name: str = 'нет_фамилии',
                                 gender: str = None,
                                 ) -> None:
        """
        Добавляет в базу данных пользователя бота, не выдаёт ролей.

        Args:
            telegram_id: telegram id
            telegram_username: telegram упоминание (username)
            first_name: Имя пользователя в боте
            last_name: Фамилия пользователя в боте
            gender: Пол, female - женский, male - мужской

        Returns:
            None: метод полностью выполнился
        """
        sql_request = f"""INSERT INTO 
                            `bot_user`(
                                    `telegram_id`, 
                                    `telegram_username`, 
                                    `first_name`, 
                                    `last_name`, 
                                    `gender`, 
                                    `is_registered`
                                ) 
                        VALUES (
                            '{telegram_id}', 
                            {chr(39) if telegram_username else ''}
                            {telegram_username if telegram_username else 'NULL'}
                            {chr(39) if telegram_username else ''},
                            '{first_name}',
                            '{last_name}',
                            {chr(39) if gender else ''}{gender if gender else 'NULL'}{chr(39) if gender else ''},
                            FALSE)"""
        await self.sql(sql_request)

    async def get_all_messages_prefix(self) -> str:
        """
        Получает префикс всех сообщений.

        Returns:
            str: Префикс
        """
        sql_request = "SELECT `value` FROM `setting` WHERE `name` = 'all_messages_prefix'"
        response = await self.sql(sql_request)
        if await is_empty(response): return ''

        data = response[0]['value']

        if data == 'bot_version':
            prefix = f'{BOT_VERSION}\n\n'
        elif data == 'None':
            prefix = ''
        else:
            prefix = data
            prefix = prefix.replace("/n", "\n")
            prefix = prefix.replace("bot_version", BOT_VERSION)
        return prefix

    async def get_terms_agree_by_telegram_id(self, telegram_id: int) -> Union[bool, None]:
        """
        Получает статус принятия условий пользования пользователем по telegram id.

        Args:
            telegram_id: telegram_id

        Returns:
            bool: True - принято, False - не приняты
            None: пользователь не найден
        """
        sql_request = f"SELECT `terms_agree` FROM `bot_user` WHERE `telegram_id`='{telegram_id}'"
        response = await self.sql(sql_request)

        if await is_empty(response): return None
        return True if response[0]['terms_agree'] else False

    async def set_terms_agree_by_telegram_id(self, telegram_id: int, value: bool = False) -> None:
        """
        Устанавливает состояния принятия условий пользования по telegram id.

        Args:
            telegram_id: telegram id
            value: True - условия приняты, False - условия не приняты

        Returns:
            None: Метод полностью выполнился
        """
        sql_request = f"UPDATE `bot_user` SET `terms_agree`={'TRUE' if value else 'FALSE'} WHERE " \
                      f"`telegram_id`='{telegram_id}'"
        await self.sql(sql_request)

    async def get_terms_text(self) -> Union[str, None]:
        """
        Получает текст пользовательского соглашения.

        Returns:
            dict: Упакованные данные ответа
        """
        sql_request = "SELECT `value` FROM `setting` WHERE `name`='terms_text'"
        response = await self.sql(sql_request)

        return None if await is_empty(response) else response[0]['value']
