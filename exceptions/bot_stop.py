#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

# ======================================================================================================================
#   Copyright (c) 2023.
#   Сайт: https://catdeveloper.com
#   Разработчик: https://catdeveloper.com/kontakty
# ======================================================================================================================

"""Класс необрабатываемого исключения."""

from create_bot import gettext as _, bot, loop


class UnhandledException(Exception):
    """Класс ошибки получения соединения с MYSQL базой данных."""

    def __init__(self, message: str) -> None:
        """
        init метод.

        Args:
            message: сообщение
        """
        self.message = _(f'[ERROR] - Не обрабатываемое исключение: "(%s)".' % message)
        with open('logs/errors_log.log', 'a', encoding='utf-8') as file:
            file.write(self.message + '\n')
        loop.stop()

    def __str__(self) -> str:
        """
        Текстовое представление класса ошибки.

        Returns:
            str: сообщение ошибки
        """
        return self.message

    async def bot_stop(self) -> None:
        """
        Выполняет остановку бота.

        Returns:
            None
        """
        await bot.close()
