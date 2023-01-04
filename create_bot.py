#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

# ======================================================================================================================
#   Copyright (c) 2022.
#   Сайт: https://catdeveloper.com
#   Разработчик: https://catdeveloper.com/kontakty
# ======================================================================================================================


"""В этом файле создаётся бот и необходимые компоненты."""

import asyncio
import os

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from aiogram.contrib.middlewares.i18n import I18nMiddleware

from config import MONGO_DATABASE_USER, MONGO_DATABASE_PASSWORD, MONGO_DATABASE_HOST, MONGO_DATABASE_PORT, \
    MONGO_DATABASE_NAME, API_TOKEN, TEXT_DOMAIN, ABS_PATH

loop = asyncio.get_event_loop()

storage = MongoStorage(
    host=MONGO_DATABASE_HOST,
    db_name=MONGO_DATABASE_NAME,
    username=MONGO_DATABASE_USER,
    password=MONGO_DATABASE_PASSWORD,
    port=MONGO_DATABASE_PORT,
)

bot = Bot(token=API_TOKEN, loop=loop)
dp = Dispatcher(bot, storage=storage)

i18n = I18nMiddleware(TEXT_DOMAIN, os.path.join(ABS_PATH, 'locales'))
gettext = i18n.gettext