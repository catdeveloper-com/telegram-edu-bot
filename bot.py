#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

# ======================================================================================================================
#   Copyright (c) 2022.
#   Сайт: https://catdeveloper.com
#   Разработчик: https://catdeveloper.com/kontakty
# ======================================================================================================================

"""Файл запускающий бота."""

from aiogram.utils import executor

from config import WEBHOOK_URL
from create_bot import dp, bot, i18n
from handlers import other
from loggers import ConsoleLogger
from middlewares.access_control import AccessControlMiddleware
from middlewares.check_install import CheckInstalledMiddleware
from middlewares.throttling import ThrottlingMiddleware


async def on_startup(_):
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(_):
    await bot.delete_webhook()


if __name__ == '__main__':
    import sys
    path = 'logs/console.log'
    sys.stdout = ConsoleLogger(path)
    dp.middleware.setup(i18n)
    dp.middleware.setup(CheckInstalledMiddleware())
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(AccessControlMiddleware())
    # student.register_handlers_client(dp)
    # lecturer.register_handlers_lecturers(dp)
    # editor.register_handlers_admin(dp)
    # admin.register_handlers_admin(dp)
    # director.register_handlers_admin(dp)
    # root.register_handlers_root(dp)
    other.register_handlers_other(dp)

    executor.start_polling(dp)
