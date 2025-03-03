from typing import Optional

import pendulum
from aiogram.types import Message
from backend.api.main.models import *
from tortoise.expressions import Q

from tg_bot.exceptions import ReplyAbortError


async def get_user(message: Message):
    assert message.from_user and message.from_user.username
    user = await User.filter(Q(chat_id=message.from_user.id) | Q(username=message.from_user.username)).first()
    if not user:
        user = await User.create(chat_id=message.from_user.id, username=message.from_user.username)
    # 更新用户名等信息
    if user.chat_id != message.from_user.id or user.username != message.from_user.username:
        user.chat_id = message.from_user.id
        user.username = message.from_user.username
        await user.save()
    return user


async def get_group(message: Message):
    return (await Group.get_or_create(chat_id=message.chat.id))[0]


async def get_daily_session(message: Message):
    group = await get_group(message)
    session = await DailySession.filter(group=group).last()
    if not session or pendulum.instance(session.started_at).end_of("day").add(hours=4) < pendulum.instance(
        message.date
    ).start_of("day"):
        raise ReplyAbortError("请先开始记账")
    return session


async def is_operator(message: Message, user: Optional[User] = None):
    group = await get_group(message)
    user = user or await get_user(message)
    return await GroupOperator.filter(group=group, user=user).exists()


async def is_bot_admin(message: Message, user: Optional[User] = None):
    user = user or await get_user(message)
    return user.is_staff
