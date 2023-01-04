#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

# ======================================================================================================================
#   Copyright (c) 2023.
#   Сайт: https://catdeveloper.com
#   Разработчик: https://catdeveloper.com/kontakty
# ======================================================================================================================

"""Middleware проверяющий доступ пользователя."""
import os
from typing import Dict, Any

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message

from config import TERMS_AGREE_PHRASE, ADMIN_GROUP_ID, SUPPORT_GROUP_ID, ABS_PATH, NO_ACCESS_MESSAGE, OWNER_ID, STICKERS
from create_custom_objects import db, mm
from create_bot import gettext as _
from exceptions.bot_stop import UnhandledException
from loggers import warnings_logger
from utils import check_user_access, get_user_roles_by_telegram_id, is_empty


class AccessControlMiddleware(BaseMiddleware):
    """Класс Middleware проверяющий доступ к командам."""

    async def on_process_message(self, event: Message, data: Dict[str, Any]) -> None:
        """
        Проверяет доступ пользователя к команде.

        Args:
            event: событие сообщения
            data: данные

        Returns:
            None
        """
        self.event = event
        self.data = data
        self.user_fsm_state = data['state']
        self.is_setup_state = not os.path.exists(os.path.join(ABS_PATH, 'bot_installed.txt'))

        if self.is_setup_state:
            return

        # Проверяем пользователя в базе данных
        user_data = await db.check_telegram_id_in_db(event.from_user.id)
        # Если пользователя нет в базе данных - заносим его туда
        if not user_data: await db.add_bot_user_in_db(event.from_user.id, event.from_user.username)
        # Если сообщение пришло из беседы или канала, кроме административных
        from_chat_id = event.chat.id
        if from_chat_id < 0 and (from_chat_id != ADMIN_GROUP_ID or from_chat_id != SUPPORT_GROUP_ID):
            raise CancelHandler

        # Если условия пользования не приняты - просим принять
        terms_agree_status = await db.get_terms_agree_by_telegram_id(event.from_user.id)
        if await is_empty(terms_agree_status):
            raise UnhandledException(
                _('Попытка проверить регистрацию не найденного пользователя в Access Middleware: '
                  'telegram_id: "%s"' % event.from_user.id)
            )
        terms_agree_text = await db.get_terms_text()
        if await is_empty(terms_agree_status):
            raise UnhandledException(
                _('Получены пустые условия пользования в Access Middleware')
            )

        if (not terms_agree_status) and (event.text != TERMS_AGREE_PHRASE):
            await mm.send_message(terms_agree_text, message_object=event)
            await mm.send_message(
                _('Если вы принимаете условия пользования, напишите: "%s"' % TERMS_AGREE_PHRASE),
                message_object=event)
            raise CancelHandler
        elif (not terms_agree_status) and (event.text == TERMS_AGREE_PHRASE):
            await db.set_terms_agree_by_telegram_id(event.from_user.id, True)

        # Получаем настройки бота, чтобы узнать режим доступа
        bot_settings = await db.get_bot_settings()
        if await is_empty(bot_settings):
            raise UnhandledException(
                _('Получены пустые настройки бота в Access Middleware')
            )

        access_mode = bot_settings['access_mode']
        if access_mode == 'allow_all':
            pass
        elif access_mode == 'strict':
            # Проверяем регистрацию пользователя
            is_register = await db.check_bot_user_registration_by_telegram_id(event.from_user.id)
            if await is_empty(is_register):
                raise UnhandledException(
                    _('Попытка проверить регистрацию не найденного пользователя в Access Middleware')
                )
            # Если пользователь не зарегистрирован
            if not is_register:
                await mm.send_message(
                    _('Регистрация ограничена, доступ есть только у зарегистрированных пользователей'),
                    message_object=event,
                )
                raise CancelHandler
            # Если пользователь зарегистрирован - запрашиваем разрешение на выполнение команды
            if event.is_command():
                access = await check_user_access(event.from_user.id, event.get_command())
                if await is_empty(access):
                    await mm.send_message(
                        _('Запрашиваемая команда не найдена в списке доступных'),
                        message_object=event,
                    )
                    raise CancelHandler
                if not access:
                    await mm.send_message(NO_ACCESS_MESSAGE, message_object=event)
                    warnings_logger.warning(
                        _('Попытка доступа к запрещённой команде: telegram_id: "%s" | команда: "%s"' % (
                            event.from_user.id,
                            event.get_command(),
                        )
                          )
                    )
                    raise CancelHandler
                return
        elif access_mode == 'debug':
            # Получаем роли пользователя
            roles = await get_user_roles_by_telegram_id(event.from_user.id)
            if await is_empty(roles):
                raise UnhandledException(
                    _('Попытка получить роли не существующего пользователя в Access Middleware')
                )
            if "admin" in roles: return
            await mm.send_message(
                _('Бот находится на техническом обслуживании, попробуйте заглянуть позже'),
                message_object=event,
                sticker_id=STICKERS['programmer coding ok']
            )
            raise CancelHandler
        else:
            raise UnhandledException(_('Передан неизвестный режим доступа в Access Middleware: "%s"' % access_mode))
