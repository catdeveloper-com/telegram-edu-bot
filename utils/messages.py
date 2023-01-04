#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

# ======================================================================================================================
#   Copyright (c) 2022.
#   Сайт: https://catdeveloper.com
#   Разработчик: https://catdeveloper.com/kontakty
# ======================================================================================================================

"""Модуль для работы с сообщениями."""
from typing import Union

from aiogram.types import Message, CallbackQuery

from config import OWNER_ID, STICKERS, ADMIN_GROUP_ID, SUPPORT_GROUP_ID, API_TOKEN, LINE_BREAK_SYMBOL, MAX_MESSAGE_LEN
from create_bot import bot, gettext as _
from loggers import errors_logger, warnings_logger, messages_logger
from utils.functions import is_empty


class MessagesManager:
    """Класс для работы с сообщениями."""

    async def send_message(self,
                           message: str = _('Пустое сообщение'),
                           message_object: Message = None,
                           callback: CallbackQuery = None,
                           chat_id: int = None,
                           reply_markup=None,
                           parse_mode: str = 'HTML',
                           sticker_id: str = None,
                           deny_none: bool = True,
                           ignore_line_break_symbol: bool = False,
                           ) -> Union[list, bool]:
        """
        Отправляет сообщение.

        Args:
            message: текст сообщения
            message_object: объект сообщения
            callback: объект callback
            chat_id: id чата получателя
            reply_markup: клавиатура
            parse_mode: режим парсинга сообщения
            sticker_id: id стикера
            deny_none: запретить слово "None"
            ignore_line_break_symbol: игнорировать символ переноса строки

        Returns:
            list: Список ответов полученных при отправке частей сообщения
            bool: False - ошибка при отправке сообщения
        """
        from create_custom_objects import db
        if message is None:
            message = _('Пустое сообщение')
        if type(message) != str:
            message = str(message)

        message = message.replace(API_TOKEN, _('[HIDDEN]'))
        if deny_none: message = message.replace('None', '---')

        ALL_MESSAGES_PREFIX = await db.get_all_messages_prefix()
        if not ignore_line_break_symbol:
            message_text = f"{ALL_MESSAGES_PREFIX}{message}".replace(LINE_BREAK_SYMBOL, "\n")
        else:
            message_text = f"{ALL_MESSAGES_PREFIX}{message}"

        # Разделение сообщений на части по MAX_MESSAGE_LEN символов, и отправка каждой части по отдельности
        messages_array = []
        for x in range(0, len(message), MAX_MESSAGE_LEN):
            messages_array.append(message_text[x:x + MAX_MESSAGE_LEN])

        # Если чат id не указан, но передан объект сообщения или callback
        if chat_id is None and (message_object or callback):
            messages_responses = []
            for message_part in messages_array:
                if message_object:
                    messages_responses.append(
                        await message_object.reply(
                            message_part,
                            reply_markup=reply_markup,
                            parse_mode=parse_mode
                        )
                    )
                else:
                    await callback.answer()
                    messages_responses.append(
                        await callback.message.answer(
                            message_part,
                            reply_markup=reply_markup,
                            parse_mode=parse_mode
                        )
                    )
            try:
                if sticker_id and message_object:
                    await message_object.answer_sticker(sticker_id)
                    messages_logger.info(_(
                        'Ответный стикер: message: True | callback: False | id: "%s"' % str(sticker_id))
                    )
                elif sticker_id and callback:
                    await callback.message.answer_sticker(sticker_id)
                    messages_logger.info(
                        _('Ответный стикер: message: False | callback: True | id: "%s"' % str(sticker_id)))
                elif sticker_id and chat_id:
                    await callback.message.answer_sticker(sticker_id)
                    messages_logger.info(
                        _(
                            'Ответный стикер: chat_id: "%s" | message: False | callback: True | id: "%s"' % (
                                chat_id, str(sticker_id)
                            )
                        )
                    )
            except Exception:
                errors_logger.exception(_('стикер не отправлен, id стикера: "%s' % sticker_id))
                await self.send_notify(OWNER_ID,
                                       _('Ошибка при отправке стикера'),
                                       'Error')
            messages_logger.info(_('Ответное сообщение: text: "%s"' % message))
            return messages_responses
        elif chat_id:
            messages_responses = []
            for message_part in messages_array:
                from create_bot import bot
                messages_responses.append(
                    await bot.send_message(chat_id, message_part, reply_markup=reply_markup, parse_mode=parse_mode))
            messages_logger.info(_('Ответное сообщение: chat_id: "%s" | text: "%s"' % (chat_id, message)))
            return messages_responses
        else:
            errors_logger.error(
                _('Ответное сообщение: error: Не передан chat_id, объект message или callback | text: "%s"' % message)
            )
            return False

    async def send_message_to_owner(self,
                                    message: str = _('Пустое сообщение для root пользователя'),
                                    sticker_key: str = None,
                                    parse_mode: str = 'HTML'
                                    ) -> None:
        """
        Отправляет сообщение root пользователю.
        Args:
            message: текст сообщения
            sticker_key: ключ стикера
            parse_mode: режим парсинга сообщения

        Returns:
            None
        """

        await bot.send_message(chat_id=OWNER_ID, message=message, parse_mode=parse_mode)
        if sticker_key:
            if sticker_key in STICKERS.keys():
                await bot.send_sticker(OWNER_ID, STICKERS[sticker_key])
            else:
                errors_logger.error(_('Стикера с ключём "%s" не существует!' % sticker_key))
                await bot.send_message(OWNER_ID, _('[ERROR] smto -> Стикера с ключём "%s" не найдено!' % sticker_key))

    async def send_notify(self,
                          chat_id: int,
                          message: str,
                          level: str = 'None',
                          prefix: str = _('Уведомление'),
                          only_start_wrapper: bool = False,
                          reply_markup=None,
                          parse_mode='HTML',
                          deny_none: bool = True
                          ) -> Union[list, bool]:
        """
        Отправляет сообщение-уведомление на указанный chat id.

        Args:
            chat_id: id чата в который нужно отправить сообщение
            message: текст сообщения
            level: уровень уведомления None - "", Success - "✅", Warning - "⚠️", Error - "❗️", Blocked - "❌"
            prefix: префикс
            only_start_wrapper: обернуть emoji только слева
            reply_markup: клавиатура
            parse_mode: режим парсинга сообщения
            deny_none: запретить отображать слово "None"

        Returns:
            list: список ответов полученных при отправке частей сообщения
            bool: False - ошибка при отправке
        """
        wrappers = {
            "None": "",
            "Success": "✅",
            "Warning": "⚠️",
            "Error": "❗️",
            "Blocked": "❌",
        }

        if not level in wrappers.keys():
            warnings_logger.warning(f'Передан не существующий уровень важности сообщения-уведомления: "{level}"')
            level = 'None'
        wrapper = wrappers[level]

        if only_start_wrapper:
            msg = f"{wrapper}{message}"
        else:
            msg = f"{wrapper}{message}{wrapper}"

        if prefix:
            msg = f"{prefix}\n\n{msg}"
        try:
            return await self.send_message(message=msg,
                                           chat_id=chat_id,
                                           reply_markup=reply_markup,
                                           parse_mode=parse_mode,
                                           deny_none=deny_none)
        except Exception:
            errors_logger.exception(_('уведомление не отправлено, текст уведомления: "%s"' % message))
            return False

    async def make_spoiler_text(self, text: str) -> str:
        """
        Делает текст спойлером, работает только для режима парсинга HTML.

        Args:
            text: текст

        Returns:
            str: Текст-спойлер
        """
        return f'<tg-spoiler>{text}</tg-spoiler>'

    async def send_message_to_admin_chat(self,
                                         message_text: str = _('Пустое сообщение для беседы администраторов'),
                                         sticker_id: str = None,
                                         parse_mode: str = 'HTML',
                                         reply_markup=None) -> Union[list, bool]:
        """
        Отправляет сообщение в беседу администраторов.

        Args:
            message_text: текст сообщения
            sticker_id: id стикера
            parse_mode: режим парсинга сообщения
            reply_markup: клавиатура

        Returns:
            list: список ответов полученных при отправке частей сообщения
            bool: False - ошибка при отправке
        """
        return await self.send_message(message=message_text,
                                       chat_id=ADMIN_GROUP_ID,
                                       parse_mode=parse_mode,
                                       reply_markup=reply_markup,
                                       sticker_id=sticker_id)

    async def send_message_to_support_chat(self,
                                           message: str = _('Пустое сообщение для беседы техподдержки'),
                                           sticker_id: str = None,
                                           parse_mode: str = 'HTML',
                                           reply_markup=None) -> Union[list, bool]:
        """
        Отправляет сообщение в беседу техподдержки.

        Args:
            message: текст сообщения
            sticker_id: id стикера
            parse_mode: режим парсинга сообщения
            reply_markup: клавиатура

        Returns:
            list: Список ответов полученных при отправке частей сообщения
            bool: False - ошибка при отправке
        """
        return await self.send_message(message=message,
                                       chat_id=SUPPORT_GROUP_ID,
                                       parse_mode=parse_mode,
                                       reply_markup=reply_markup,
                                       sticker_id=sticker_id)

    async def spam(self,
                   telegram_ids: list,
                   message_text: str = _('Пустое сообщение для рассылки'),
                   sticker_id: str = None,
                   parse_mode='HTML',
                   render_log: bool = True,
                   return_only_counters: bool = True,
                   files: dict = None,
                   deny_none: bool = True,
                   reply_markup=None) -> Union[str, dict, None]:
        """
        Рассылает сообщение на указанные telegram_id.

        Args:
            telegram_ids: список telegram id
            message_text: Текст сообщения
            sticker_id: id стикера
            parse_mode: режим парсинга сообщения
            render_log: True - вернуть логи в виде телеграм сообщения, False - вернуть логи в виде списков
            return_only_counters: True - Вернуть только количество отправленных сообщений, False - вернёт render_log
            files: словарь с файлами для рассылки
            deny_none: запретить слово "None"
            reply_markup: Клавиатура

        Returns:
            str: отчёт о рассылке
            dict: словарь с логом успешных отправок и ошибок
            None: передан пустой список telegram id
        """
        if await is_empty(telegram_ids): return None
        success_log, errors_log = [], []

        for telegram_id in telegram_ids:
            not_telegram_id_message = _('"%s" - не является id' % telegram_id)
            if type(telegram_id) == str:
                if not telegram_id.isdigit():
                    errors_log.append(not_telegram_id_message)
                    continue
            elif type(telegram_id) == int:
                pass
            else:
                errors_log.append(not_telegram_id_message)
                continue

            try:
                await self.send_message(message=message_text,
                                        chat_id=telegram_id,
                                        reply_markup=reply_markup,
                                        sticker_id=sticker_id,
                                        parse_mode=parse_mode,
                                        deny_none=deny_none)
                if files:
                    from create_bot import bot
                    for key, file in files.items():
                        if key == 'photo':
                            await bot.send_photo(telegram_id, file)
                        elif key == 'video':
                            await bot.send_video(telegram_id, file)
                        elif key == 'doc':
                            await bot.send_document(telegram_id, file)
                success_log.append(_('"%s" - Успех') % telegram_id)
            except Exception as e:
                errors_logger.exception(
                    _(
                        'рассылка: Ошибка при отправке сообщения: text: "%s" | '
                        'telegram_id: "%s"' % (message_text, telegram_id)
                    )
                )
                errors_log.append(_('telegram_id: "%s" - Ошибка: "%s"' % (telegram_id, e)))
        if return_only_counters:
            return _('Рассылка завершена, сообщения получили %s/%s:\n\n' \
                     '- Успешно отправлено: %s\n- Ошибка отправки: %s' % (len(success_log), len(telegram_ids),
                                                                              len(success_log), len(errors_log)))
        if render_log:
            s_msg = '\n'.join(success_log)
            e_msg = '\n'.join(errors_log)
            return _('Успех (%s):\n\n%s\n\nОшибка отправки(%s):\n\n%s' % (
                len(success_log),
                s_msg if len(errors_log) != 0 else '---',
                len(errors_log),
                e_msg if len(errors_log) != 0 else '---')
                    )
        return {'errors_list': errors_log, 'success_list': success_log}
