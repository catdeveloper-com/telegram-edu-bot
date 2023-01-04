#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

# ======================================================================================================================
#   Copyright (c) 2023.
#   Сайт: https://catdeveloper.com
#   Разработчик: https://catdeveloper.com/kontakty
# ======================================================================================================================

"""Тут создаются Логгеры."""
import sys

from aiologger import Logger
from aiologger.formatters.base import Formatter
from aiologger.handlers.files import AsyncFileHandler
from aiologger.levels import LogLevel

formatter = Formatter('[%(levelname)s] [%(asctime)s] [%(filename)s -> %(funcName)s line:%(lineno)d] %(message)s')

warnings_logger = Logger(name="Errors_logger", level=LogLevel.WARNING)
handler = AsyncFileHandler(filename='logs/warnings_log.log', mode='a', encoding="UTF-8")
handler.formatter = formatter
warnings_logger.add_handler(handler)

errors_logger = Logger(name="Errors_logger", level=LogLevel.ERROR)
handler = AsyncFileHandler(filename='logs/errors_log.log', mode='a', encoding="UTF-8")
handler.formatter = formatter
errors_logger.add_handler(handler)

messages_logger = Logger(name="Messages_logger", level=LogLevel.INFO)
handler = AsyncFileHandler(filename='logs/messages_log.log', mode='a', encoding="UTF-8")
handler.formatter = formatter
messages_logger.add_handler(handler)


class ConsoleLogger:

    def __init__(self, filename):
        self.console = sys.stdout
        self.file = open(filename, 'w')

    def write(self, message):
        self.console.write(message)
        self.file.write(message)

    def flush(self):
        self.console.flush()
        self.file.flush()