import functools
from typing import cast

from aiogram.types import CallbackQuery, Message

from .backend import sdk
from .exceptions import ReplyAbortError
from .utils import is_chat_admin, is_group


def require_bot_admin(func):
    @functools.wraps(func)
    async def wrapper(message: Message | CallbackQuery, *args, **kwargs):
        if isinstance(message, Message):
            _message = message
        else:
            assert message.message
            _message = cast(Message, message.message)
        if await sdk.is_bot_admin(_message):
            return await func(message, *args, **kwargs)
        return await _message.reply("没有权限执行此操作")

    return wrapper


def require_group(func):
    @functools.wraps(func)
    async def wrapper(message: Message | CallbackQuery, *args, **kwargs):
        if isinstance(message, Message):
            _message = message
        else:
            assert message.message
            _message = cast(Message, message.message)
        if await is_group(_message):
            return await _message.reply("只能在群组中执行此操作")
        return await func(message, *args, **kwargs)

    return wrapper


def require_admin(func):
    @functools.wraps(func)
    async def wrapper(message: Message | CallbackQuery, *args, **kwargs):
        if isinstance(message, Message):
            _message = message
        else:
            assert message.message
            _message = cast(Message, message.message)
        if await sdk.is_operator(_message) or await is_chat_admin(_message):
            return await func(message, *args, **kwargs)
        return await _message.reply("只有操作员和管理员可以执行此操作")

    return wrapper


def error_handler(func):
    @functools.wraps(func)
    async def wrapper(message: Message | CallbackQuery, *args, **kwargs):
        if isinstance(message, Message):
            _message = message
        else:
            assert message.message
            _message = cast(Message, message.message)
        try:
            return await func(message, *args, **kwargs)
        except ReplyAbortError as e:
            return await _message.reply(str(e))

    return wrapper
