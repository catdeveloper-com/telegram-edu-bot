#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

# ======================================================================================================================
#   Copyright (c) 2022.
#   Сайт: https://catdeveloper.com
#   Разработчик: https://catdeveloper.com/kontakty
# ======================================================================================================================

"""Функции для работы с датой и временем."""
from datetime import datetime
from typing import Union

from pytz import timezone

from config import TIMEZONE
from utils import is_empty


async def get_current_time() -> datetime.now:
    """
    Получает текущее время

    Returns:
        datetime.now: datetime.now
    """
    return datetime.now(timezone(TIMEZONE))


async def get_current_day_number() -> int:
    """
    Получает порядковый номер текущего дня недели, первый день недели - понедельник

    Returns:
        int: порядковый номер дня недели
    """
    return datetime.now(timezone(TIMEZONE)).isoweekday()


async def get_week_type(institution_id: int) -> Union[bool, None]:
    """
    Получает тип недели.

    Args:
        institution_id: id учебного заведения

    Returns:
        bool: True - числитель, False - знаменатель
        None: не найдено учебное заведение с таким id
    """
    from create_custom_objects import db

    cur_week_num = int(datetime.now().strftime("%V"))
    response = await db.sql(f"SELECT `invert_week_type` FROM `institution` WHERE `id` = '{institution_id}'")
    if await is_empty(response): return None

    if response[0]['invert_week_type']:
        if cur_week_num % 2 == 0:
            return False
        return True
    if cur_week_num % 2 == 0:
        return True
    return False
