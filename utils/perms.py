#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

# ======================================================================================================================
#   Copyright (c) 2022.
#   Сайт: https://catdeveloper.com
#   Разработчик: https://catdeveloper.com/kontakty
# ======================================================================================================================

"""Функции для работы с разрешениями."""
from typing import Union

from utils import is_empty
from utils.users import get_user_roles_by_telegram_id


async def get_roles_priority(return_role_id_priority: bool = False) -> Union[dict, None]:
    """
    Получает приоритеты ролей.

    Args:
        return_role_id_priority: True - вернёт словарь {id_роли:приоритет_роли}, False - {название_роли:приоритет_роли}

    Returns:
        dict: словарь с приоритетом ролей
    """
    from create_custom_objects import db

    sql_request = f"SELECT * FROM `bot_role` ORDER BY `priority` DESC"
    response = await db.sql(sql_request)
    if await is_empty(response): return None
    roles_priority = {}
    for item in response:
        if return_role_id_priority:
            roles_priority.update({item['id']: item['priority']})
        else:
            roles_priority.update({item['name']: item['priority']})
    return roles_priority


async def get_perms_by_telegram_id(telegram_id: int) -> Union[list, None]:
    """
    Получает набор разрешений по telegram id.

    Args:
        telegram_id: telegram_id

    Returns:
        list: Список разрешенных команд
        None: ничего не найдено
    """
    from create_custom_objects import db

    bot_user_id = await db.telegram_id_to_bot_user_id(telegram_id)
    roles_ids = await get_user_roles_by_telegram_id(telegram_id, return_only_ids=True)
    roles_priority = await get_roles_priority(return_role_id_priority=True)
    perms = await db.sql(f"SELECT * FROM `permission`")

    if (await is_empty(bot_user_id)) or (await is_empty(roles_ids)) \
            or (await is_empty(roles_priority)) or (await is_empty(perms)): return None

    always_allow, always_deny = [], []
    roles_allow, roles_deny = {}, {}

    for line in perms:
        # Если разрешение персонально для пользователя
        if line['for_bot_user_id'] == bot_user_id:
            # Если поле deny_command не пустое - добавить команду в список всегда запрещённых
            if not (line['deny_command'] is None or line['deny_command'] == ""):
                always_deny.append(line['deny_command'])
            # Иначе добавить в список всегда разрешенных команд
            else:
                always_allow.append(line['allow_command'])
        # Иначе, если разрешение для роли
        else:
            # Если роль не принадлежит пользователю - новая итерация
            if not line['for_bot_role_id'] in roles_ids:
                continue
            # Если роль принадлежит пользователю - получаем её приоритет
            role_priority = roles_priority[line['for_bot_role_id']]
            # Если поле deny_command не пустое
            if not (line['deny_command'] is None or line['deny_command'] == ""):
                # Если в словаре запрещено_для_роли нет ключа role_priority
                if not role_priority in roles_deny:
                    # Добавляем ключ role_priority: [запрещенная_команда, ]
                    roles_deny.update({role_priority: [line['deny_command'], ]})
                # Если ключ есть -
                else:
                    # добавляем команду в список запрещённых для роли
                    roles_deny[role_priority].append(line['deny_command'])
                # Проверим разрешено_для_роли, если нет такого ключа role_priority - добавим
                if not role_priority in roles_allow:
                    roles_allow.update({role_priority: []})
            # Если поле deny_command пустое, то поле allow_command заполнено
            else:
                # Если в словаре разрешено_для_роли нет ключа role_priority
                if not role_priority in roles_allow:
                    # Добавляем ключ role_priority: [разрешенная_команда, ]
                    roles_allow.update({role_priority: [line['allow_command'], ]})
                # Если ключ есть -
                else:
                    # Добавляем команду в список разрешенных для роли
                    roles_allow[role_priority].append(line['allow_command'])
                # Проверим запрещено_для_роли, если нет такого ключа role_priority - добавим
                if not role_priority in roles_deny:
                    roles_deny.update({role_priority: []})

    # Проходим приоритет, разрешенная_команда в разрешено_для_роли
    for role_priority, item in roles_allow.items():
        # Проходим индекс, разрешенная_команда в enumerate(item)
        for index, command in enumerate(item):
            # Если команда_разрешена_для_роли есть в списке всегда_запрещено - удаляем из разрешенных
            if command in always_deny:
                del roles_allow[role_priority][index]

    # Проходим приоритет, запрещенная_команда в запрещено_для_роли
    for role_priority, item in roles_deny.items():
        # Проходим индекс, запрещенная_команда в enumerate(item)
        for index, command in enumerate(item):
            # Если команда_запрещена_для_роли есть в списке всегда_разрешено - удаляем из запрещенных
            if command in always_allow:
                del roles_deny[role_priority][index]

    # Получаем сортированный по убыванию список приоритетов ролей
    roles_allow_keys = sorted(roles_allow.keys(), reverse=True)

    # финальные списки
    final_allow_commands, final_deny_commands = [], []

    # Проходим индекс, приоритет в enumerate(roles_allow_keys)
    for index, role_priority in enumerate(roles_allow_keys):
        # Если индекс == 0, то есть самая высокая роль пользователя
        if index == 0:
            # Добавляем все разрешенные самой высокой ролью команды в финальный список разрешенных
            final_allow_commands.extend(roles_allow[role_priority])
            # Добавляем все запрещенные самой высокой ролью команды в финальный список запрещенных
            final_deny_commands.extend(roles_deny[role_priority])
        # Иначе, если не самая высокая роль пользователя
        else:
            # Проходим запрещенная_команда в запрещено_для_роли[приоритет_текущей_роли]
            for command in roles_deny[role_priority]:
                # Если запрещенная_команда есть в финальном списке разрешенных - новая итерация
                if command in final_allow_commands:
                    continue
                # Если команда не разрешена на более высоком уровне - добавляем в финальный список запрещённых
                else:
                    final_deny_commands.append(command)

            # Проходим разрешенная_команда в разрешено_для_роли[приоритет_текущей_роли]
            for command in roles_allow[role_priority]:
                # Если разрешенная_команда есть в финальном списке запрещенных - новая итерация
                if command in final_deny_commands:
                    continue
                # Если команда не запрещена на более высоком уровне - добавляем в финальный список разрешенных
                else:
                    final_allow_commands.append(command)
    return list(set(final_allow_commands))


async def check_user_access(telegram_id: int, command_name: str) -> Union[bool, None]:
    """
    Проверяет доступ пользователя к команде.

    Args:
        telegram_id: telegram id
        command_name: имя запрошенной команды

    Returns:
        bool: True - доступ разрешен, False - Доступ запрещён
        None: команда не найдена
    """
    if await is_empty(command_name): return None

    allow_commands_list = await get_perms_by_telegram_id(telegram_id)
    if await is_empty(allow_commands_list): return None

    if ("all" in allow_commands_list) or (command_name in allow_commands_list): return True
    return False


async def compare_access_by_ids(telegram_id_1: int, telegram_id_2: int) -> Union[int, bool, None]:
    """
    Сравнивает 2 пользователей по правам, выдаёт telegram id пользователя с наивысшими правами, если права равны - None

    Args:
        telegram_id_1: telegram id первого пользователя
        telegram_id_2: telegram id второго пользователя

    Returns:
        int: telegram id пользователя с наивысшими правами
        bool: False - не удалось получить данные
        None: права доступа равны
    """
    roles_1 = await get_user_roles_by_telegram_id(telegram_id_1, with_roles_priority=True)
    roles_2 = await get_user_roles_by_telegram_id(telegram_id_2, with_roles_priority=True)

    if (await is_empty(roles_1)) or (await is_empty(roles_2)): return False

    max_1 = max(roles_1.keys())
    max_2 = max(roles_2.keys())
    if max_1 > max_2:
        return telegram_id_1
    elif max_1 < max_2:
        return telegram_id_2
    else:
        return None


async def system_add_user_roles_by_telegram_id(telegram_id: int, roles_ids: list) -> Union[bool, None]:
    """
    Добавляет роли пользователю по telegram id от имени системы.

    Args:
        telegram_id: telegram id
        roles_ids: список id ролей которые нужно назначить пользователю

    Returns:
        bool: False - пользователь не найден
        None: функция полностью выполнилась
    """
    from create_custom_objects import db

    bot_user_id = await db.telegram_id_to_bot_user_id(telegram_id)
    if await is_empty(bot_user_id): return False

    sql_requests = []
    for role_id in roles_ids:
        sql_request = f"INSERT INTO `bot_user_bot_role`(`bot_user_id`, `bot_role_id`) VALUES " \
                      f"('{bot_user_id}', '{role_id}')"
        sql_requests.append(sql_request)
    await db.sql_transaction(sql_requests)
