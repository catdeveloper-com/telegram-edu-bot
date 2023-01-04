#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

# ======================================================================================================================
#   Copyright (c) 2023.
#   Сайт: https://catdeveloper.com
#   Разработчик: https://catdeveloper.com/kontakty
# ======================================================================================================================

"""Функции для работы с пользователями."""
from typing import Union

from utils import is_empty


async def register_bot_user_by_telegram_id(telegram_id: int) -> None:
    """
    Регистрирует пользователя по telegram id.

    Args:
        telegram_id: telegram id

    Returns:
        None: метод полностью выполнился
    """
    from create_custom_objects import db

    sql_request = f"UPDATE `bot_user` SET `is_registered` = TRUE WHERE `telegram_id` = '{telegram_id}'"
    await db.sql(sql_request)


async def get_user_roles_by_telegram_id(telegram_id: int,
                                        with_roles_priority: bool = False,
                                        return_only_ids: bool = False) -> Union[list, dict, None]:
    """
    Получает список ролей пользователя по telegram id.

    Args:
        telegram_id: telegram id
        with_roles_priority: True - вернёт список ролей с их приоритетом, False - вернёт список ролей
        return_only_ids: True - вернёт id ролей, False - вернёт with_roles_priority

    Returns:
        list: список названий ролей
        dict: словарь вида {приоритет_роли:название_роли}
        None: роли не найдены
    """
    from create_custom_objects import db

    roles_ids_request = f"SELECT `bot_role_id` FROM `bot_user_bot_role` WHERE `bot_user_id`=(SELECT `id` FROM " \
                        f"`bot_user` WHERE `telegram_id`='{telegram_id}')"
    roles_ids_response = await db.sql(roles_ids_request)
    if await is_empty(roles_ids_response): return None

    roles_ids = [str(x['bot_role_id']) for x in roles_ids_response]
    if return_only_ids: return roles_ids

    args = "','".join(roles_ids)
    sql_request = f"SELECT `name`, `priority` FROM `bot_role` WHERE `id` IN ('{args}')"
    response = await db.sql(sql_request)

    if await is_empty(response): return None

    if with_roles_priority:
        user_roles = {}
        for item in response['data']:
            user_roles.update({item['priority']: item['name']})
    else:
        user_roles = []
        for item in response:
            user_roles.append(item['name'])
    return user_roles
