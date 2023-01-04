#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

# ======================================================================================================================
#   Copyright (c) 2022.
#   Сайт: https://catdeveloper.com
#   Разработчик: https://catdeveloper.com/kontakty
# ======================================================================================================================

"""Модуль для работы с функциями."""


async def is_empty(data: any) -> bool:
    """
    Проверяет на пустоту data .

    Args:
        data: данные для проверки

    Returns:
        bool: True - данные пусты, иначе False
    """
    if (data == ()) or (data is None) or (data == []) or (data == ''): return True
    return False
