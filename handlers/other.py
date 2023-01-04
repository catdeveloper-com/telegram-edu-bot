#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

# ======================================================================================================================
#   Copyright (c) 2022.
#   Сайт: https://catdeveloper.com
#   Разработчик: https://catdeveloper.com/kontakty
# ======================================================================================================================

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from config import NO_PROCESS_FOR_CANCEL_MESSAGE, PROCESS_CANCELED_BY_USER_MESSAGE, OWNER_ID
from middlewares.throttling import rate_limit


@rate_limit(1, 'start')
async def echo(message: types.Message):
    await message.answer('ping')


async def callback_none_func(callback: types.CallbackQuery):
    from_user_id = callback.from_user.id
    # user_state = await get_user_access_state(from_user_id, None, None, False, callback)
    # if user_state[0]:
    #     await callback.answer("⚠️Элемент не действителен⚠️", show_alert=True)
    # else:
    #     await callback.answer()


async def operation_cancel(message: types.Message, state: FSMContext):
    from_user_id = message.from_user.id
    # user_state = await get_user_access_state(from_user_id, message, 'cancel', True)
    # if user_state[0]:
    #     if await state.get_state() is None:
    #         await send_message(NO_PROCESS_FOR_CANCEL_MESSAGE, message, reply_markup=remove_kb)
    #         return
    #     await state.finish()
    #     await send_message(PROCESS_CANCELED_BY_USER_MESSAGE, message, reply_markup=remove_kb)


async def command_home(message: types.Message):
    from_user_id = message.from_user.id
    # user_state = await get_user_access_state(from_user_id, message, None)
    # if user_state[0]:
    #     kb = await get_home_keyboard_by_id(from_user_id)
    #     await send_message("Личный кабинет", message, reply_markup=kb[1])


async def dev(message: types.Message):
    from_user_id = message.from_user.id
    # if int(from_user_id) == OWNER_ID:
    #     await schedule_appender()


async def accept_terms_agree(message: types.Message):
    from_user_id = message.from_user.id
    # user_state = await get_user_access_state(from_user_id, message, None)
    # if user_state[0]:
    #     query = f"""UPDATE `User` SET terms_agree="true" WHERE user_id={from_user_id};"""
    #     response = await sql_update(query)
    #     if response[0]:
    #         await send_message("Готово, теперь вы можете пользоваться ботом", message)
    #     else:
    #         await send_message("Произошла ошибка при подтверждении согласия с условиями пользования, администратор уведомлён о проблеме")
    #         await send_notify(message=f"Ошибка при подтвеждении условий пользования: id - {from_user_id}, Ошибка: {response[1]}", chat_id=config.ADMIN_GROUP_ID, level="w")


def register_handlers_other(dp: Dispatcher):
    # dp.register_message_handler(dev, commands=['m437dev'])
    # dp.register_message_handler(command_home, commands="home")
    # dp.register_message_handler(accept_terms_agree, Text(equals=config.TERMS_AGREE_PHRASE, ignore_case=True))
    # dp.register_callback_query_handler(callback_none_func, state="*")
    dp.register_message_handler(echo)