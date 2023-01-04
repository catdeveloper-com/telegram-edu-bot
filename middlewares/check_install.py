#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

# ======================================================================================================================
#   Copyright (c) 2022.
#   Сайт: https://catdeveloper.com
#   Разработчик: https://catdeveloper.com/kontakty
# ======================================================================================================================

"""Middleware проверяющий наличие выполненной установки."""
import os.path
from typing import Any, Dict

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message

from config import ABS_PATH, OWNER_ID
from create_custom_objects import db
from loggers import messages_logger
from create_bot import gettext as _
from utils import is_empty


class CheckInstalledMiddleware(BaseMiddleware):
    """Класс middleware, проверяет установку бота."""

    async def on_process_message(self, event: Message, data: Dict[str, Any]) -> None:
        """
        Получает событие сообщения, проверяет выполнение установки, если установка не выполнена - запускает установку.

        Args:
            event: событие сообщения
            data: данные

        Returns:
            None
        """
        self.event = event
        messages_logger.info(
            _('Входящее сообщение: telegram_id: %s | telegram_username: '
              '"@%s" | text: "%s"' % (event.from_user.id,
                                          event.from_user.username if event.from_user.username else '',
                                          event.text)
              )
        )
        self.data = data
        if not os.path.exists(os.path.join(ABS_PATH, 'bot_installed.txt')):
            if self.event.text == _('Продолжить'):
                await self.run_bot_setup()
            else:
                await self.event.answer(_('Привет! Необходимо выполнить процесс установки. ВАЖНО: `база данных не должна '
                                        'содержать таблиц, иначе будут ошибки`, если вы уверены что база данных пуста '
                                        'и готовы к продолжению установки - напишите "Продолжить"'),
                                        parse_mode='markdown')
                raise CancelHandler

    async def run_bot_setup(self) -> None:
        """
        Запускает установку бота.

        Returns:
            None
        """
        message = await self.event.answer('`|▒▒▒▒▒▒▒▒▒▒| 0% | ' + _('Установка - Начинаю процесс установки`'),
                                          parse_mode='markdown')
        root_username = self.event.from_user.username

        await message.edit_text('`|██▒▒▒▒▒▒▒▒| 20% | ' + _('Установка - Заполняю базу данных таблицами...`'),
                                parse_mode="markdown")

        sql_requests = [
            'CREATE TABLE IF NOT EXISTS institution (id BIGINT NOT NULL AUTO_INCREMENT, name VARCHAR(256) NOT NULL, '
            'invert_week_type BOOLEAN NOT NULL DEFAULT FALSE, PRIMARY KEY (id), UNIQUE(id))',

            'CREATE TABLE IF NOT EXISTS setting (id BIGINT NOT NULL AUTO_INCREMENT, name VARCHAR(256) NOT NULL, '
            'value TEXT NOT NULL, PRIMARY KEY (id), UNIQUE(id), UNIQUE(name))',

            'CREATE TABLE IF NOT EXISTS lecturer (id BIGINT NOT NULL AUTO_INCREMENT, first_name VARCHAR(256) NOT NULL, '
            'last_name VARCHAR(256) NOT NULL, PRIMARY KEY (id), UNIQUE(id))',

            'CREATE TABLE IF NOT EXISTS students_group (id BIGINT NOT NULL AUTO_INCREMENT, name VARCHAR(256) NOT NULL, '
            'leader_lecturer_id BIGINT NOT NULL, PRIMARY KEY (id), UNIQUE(id), FOREIGN KEY (leader_lecturer_id) '
            'REFERENCES lecturer (id) ON DELETE RESTRICT )',

            'CREATE TABLE IF NOT EXISTS bot_user (id BIGINT NOT NULL AUTO_INCREMENT, telegram_id VARCHAR(256) '
            'NOT NULL, telegram_username VARCHAR(256), first_name VARCHAR(256) NOT NULL, last_name VARCHAR(256) '
            'NOT NULL, gender VARCHAR(128), is_registered BOOLEAN NOT NULL DEFAULT FALSE, terms_agree BOOLEAN NOT NULL '
            'DEFAULT FALSE, PRIMARY KEY (id), UNIQUE(id), UNIQUE(telegram_id))',

            'CREATE TABLE IF NOT EXISTS cabinet (id BIGINT NOT NULL AUTO_INCREMENT, name VARCHAR(256) NOT NULL, '
            'PRIMARY KEY (id), UNIQUE(id))',

            'CREATE TABLE IF NOT EXISTS specialization (id BIGINT NOT NULL AUTO_INCREMENT, name VARCHAR(256) NOT NULL, '
            'institution_id BIGINT NOT NULL, PRIMARY KEY (id), UNIQUE(id), FOREIGN KEY (institution_id) REFERENCES '
            'institution (id) ON DELETE CASCADE )',

            'CREATE TABLE IF NOT EXISTS pair (id BIGINT NOT NULL AUTO_INCREMENT, name VARCHAR(256) NOT NULL, '
            'specialization_id BIGINT NOT NULL, PRIMARY KEY (id), UNIQUE(id), FOREIGN KEY (specialization_id) '
            'REFERENCES specialization (id) ON DELETE RESTRICT )',

            'CREATE TABLE IF NOT EXISTS bot_role (id BIGINT NOT NULL AUTO_INCREMENT, name VARCHAR(256) NOT NULL, '
            'priority BIGINT NOT NULL, PRIMARY KEY (id), UNIQUE(id), CONSTRAINT u_bot_role_priority UNIQUE (`name`, '
            '`priority`))',

            'CREATE TABLE IF NOT EXISTS permission (id BIGINT NOT NULL AUTO_INCREMENT, allow_command VARCHAR(256), '
            'deny_command VARCHAR(256), for_bot_user_id BIGINT, for_bot_role_id BIGINT, PRIMARY KEY (id), UNIQUE(id), '
            'FOREIGN KEY (for_bot_user_id) REFERENCES bot_user(id) ON DELETE CASCADE , FOREIGN KEY (for_bot_role_id) '
            'REFERENCES bot_role (id) ON DELETE CASCADE )',

            'CREATE TABLE IF NOT EXISTS schedule_change (id BIGINT NOT NULL AUTO_INCREMENT, photo_id TEXT, '
            'PRIMARY KEY (id), UNIQUE(id))',

            'CREATE TABLE IF NOT EXISTS schedule (id BIGINT NOT NULL AUTO_INCREMENT, students_group_id BIGINT NOT NULL,'
            ' lecturer_id BIGINT NOT NULL, pair_id BIGINT NOT NULL, cabinet_id BIGINT, day_number INT NOT NULL, '
            'week_type BOOLEAN NOT NULL, pair_start_time TIME NOT NULL, pair_close_time TIME NOT NULL, '
            'PRIMARY KEY (id), UNIQUE(id), FOREIGN KEY (students_group_id) REFERENCES students_group (id) ON DELETE CASCADE , '
            'FOREIGN KEY (lecturer_id) REFERENCES lecturer (id) ON DELETE RESTRICT , FOREIGN KEY (pair_id) '
            'REFERENCES pair (id) ON DELETE CASCADE , FOREIGN KEY (cabinet_id) REFERENCES cabinet (id) ON DELETE '
            'RESTRICT )',

            # Промежуточные таблицы

            'CREATE TABLE IF NOT EXISTS institution_lecturer (id BIGINT NOT NULL AUTO_INCREMENT, '
            'institution_id BIGINT NOT NULL, lecturer_id BIGINT NOT NULL, PRIMARY KEY (id), UNIQUE(id), '
            'FOREIGN KEY (institution_id) REFERENCES institution(id) ON DELETE CASCADE, '
            'FOREIGN KEY (lecturer_id) REFERENCES lecturer(id) ON DELETE CASCADE, '
            'CONSTRAINT u_institution_id_lecturer_id UNIQUE(institution_id, lecturer_id))',

            'CREATE TABLE IF NOT EXISTS institution_students_group (id BIGINT NOT NULL AUTO_INCREMENT, '
            'institution_id BIGINT NOT NULL, students_group_id BIGINT NOT NULL, PRIMARY KEY (id), '
            'FOREIGN KEY (institution_id) REFERENCES institution(id) ON DELETE CASCADE, '
            'FOREIGN KEY (students_group_id) REFERENCES students_group (id) ON DELETE CASCADE,'
            'CONSTRAINT u_institution_id_students_group_id UNIQUE(institution_id, students_group_id))',

            'CREATE TABLE IF NOT EXISTS institution_bot_user (id BIGINT NOT NULL AUTO_INCREMENT, '
            'institution_id BIGINT NOT NULL, bot_user_id BIGINT NOT NULL, PRIMARY KEY (id), '
            'FOREIGN KEY (institution_id) REFERENCES institution(id) ON DELETE CASCADE, '
            'FOREIGN KEY (bot_user_id) REFERENCES bot_user (id) ON DELETE CASCADE,'
            'CONSTRAINT u_institution_id_bot_user_id UNIQUE(institution_id, bot_user_id))',

            'CREATE TABLE IF NOT EXISTS institution_cabinet (id BIGINT NOT NULL AUTO_INCREMENT, '
            'institution_id BIGINT NOT NULL, cabinet_id BIGINT NOT NULL, PRIMARY KEY (id), '
            'FOREIGN KEY (institution_id) REFERENCES institution(id) ON DELETE CASCADE, '
            'FOREIGN KEY (cabinet_id) REFERENCES cabinet (id) ON DELETE CASCADE,'
            'CONSTRAINT u_institution_id_cabinet_id UNIQUE(institution_id, cabinet_id))',

            'CREATE TABLE IF NOT EXISTS bot_user_students_group (id BIGINT NOT NULL AUTO_INCREMENT, '
            'bot_user_id BIGINT NOT NULL, students_group_id BIGINT NOT NULL, PRIMARY KEY (id), '
            'FOREIGN KEY (bot_user_id) REFERENCES bot_user(id) ON DELETE CASCADE, '
            'FOREIGN KEY (students_group_id) REFERENCES students_group (id) ON DELETE CASCADE,'
            'CONSTRAINT u_bot_user_id_students_group_id UNIQUE(bot_user_id, students_group_id))',

            'CREATE TABLE IF NOT EXISTS bot_user_bot_role (id BIGINT NOT NULL AUTO_INCREMENT, '
            'bot_user_id BIGINT NOT NULL, bot_role_id BIGINT NOT NULL, PRIMARY KEY (id), '
            'FOREIGN KEY (bot_user_id) REFERENCES bot_user(id) ON DELETE CASCADE, '
            'FOREIGN KEY (bot_role_id) REFERENCES bot_role (id) ON DELETE CASCADE,'
            'CONSTRAINT u_bot_user_id_bot_role_id UNIQUE(bot_user_id, bot_role_id))',

            # Создаём роли пользователей
            "INSERT INTO bot_role (`name`, `priority`) VALUES ('root', '1000')",
            "INSERT INTO bot_role (`name`, `priority`) VALUES ('director', '500')",
            "INSERT INTO bot_role (`name`, `priority`) VALUES ('admin', '100')",
            "INSERT INTO bot_role (`name`, `priority`) VALUES ('editor', '50')",
            "INSERT INTO bot_role (`name`, `priority`) VALUES ('student', '10')",
            "INSERT INTO bot_role (`name`, `priority`) VALUES ('guest', '5')",
            # Создаём первого пользователя и регистрируем его
            f'INSERT INTO bot_user (telegram_id, telegram_username, first_name, last_name, is_registered, terms_agree) '
            f'VALUES ("{OWNER_ID}", "{root_username}", "нет_имени", "нет_фамилии", TRUE, TRUE)',
            # Выдаём пользователю роль root
            'INSERT INTO bot_user_bot_role (bot_user_id, bot_role_id) VALUES (1, 1)',
            # Создаём учебное заведение
            'INSERT INTO institution(name) VALUES ("Главное учебное заведение")',
            # Создаём базовые условия пользования, обязательно измените их!
            "INSERT INTO setting (name, value) VALUES ('terms_text', 'Условия пользования: мы храним историю сообщений и "
            "имеем к ней полный доступ, доступ к истории сообщений не зависит от вашего одобрения и согласия. "
            "Условия пользования могут измениться в любой момент, без уведомления вас об этом."
            "Продолжая использовать бота, вы соглашаетесь с этими условиями пользования.')",
            # Устанавливаем режим доступа
            "INSERT INTO setting (name, value) VALUES ('access_mode', 'allow_all')",
            # Привязываем root пользователя к учебному заведению
            "INSERT INTO institution_bot_user(institution_id, bot_user_id) VALUES (1, 1)"
        ]

        response = await db.sql_transaction(sql_requests)
        if await is_empty(response):
            await message.edit_text('`|████▒▒▒▒▒▒| 40% | ' + _('Установка - База данных заполнена`'),
                                    parse_mode='markdown')
            await message.edit_text('`|██████▒▒▒▒| 60% | ' + _('Установка - Роль root создана, владельцу бота назначена'
                                                               ' роль root`'),
                                    parse_mode='markdown')
            await message.edit_text('`|████████▒▒| 80% | ' + _('Установка - Создано базовое учебное заведение`'),
                                    parse_mode='markdown')
            await self.finish_setup()
            await message.edit_text('`|██████████| 100% | ' + _('Установка - Готово!`'),
                                    parse_mode='markdown')
        else:
            await message.edit_text(
                _('Ошибка при заполнении таблицами! Попробуйте отчистить базу данных от таблиц и запустить процесс '
                  'установки заново'))
            raise CancelHandler

    async def finish_setup(self) -> None:
        """
        Завершает установку бота.

        Returns:
            None
        """
        with open('bot_installed.txt', 'w', encoding='utf-8') as file:
            file.write('# ' + _('Это служебный файл, если его удалить, то бот начнёт процедуру установки'))
