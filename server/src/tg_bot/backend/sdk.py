from decimal import Decimal
from typing import Optional, cast

import pendulum
from aiogram import html
from aiogram.types import CallbackQuery, Message
from backend.api.db import redis_client
from backend.api.main import cache
from backend.api.main.models import *
from project.env import web_settings
from tg_bot.exceptions import ReplyAbortError
from tg_bot.templates import reply_bill
from tortoise.expressions import Q


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


async def list_operators(message: Message):
    group = await get_group(message)
    operators = await GroupOperator.filter(group=group)
    operator_usernames = [(await op.user.first()).username for op in operators]
    if not operator_usernames:
        return await message.reply("没有操作人")
    await message.reply(f"操作人: @{', @'.join(operator_usernames)}")


async def add_operator(message: Message, usernames: list[str]):
    for username in usernames:
        group = await get_group(message)
        user = (await User.get_or_create(username=username))[0]
        await GroupOperator.create(group=group, user=user)
    await message.reply(f"已添加操作人 @{', @'.join(usernames)}")


async def remove_operator(message: Message, usernames: list[str]):
    for username in usernames:
        group = await get_group(message)
        user = await User.get_or_none(username=username)
        if user:
            await GroupOperator.filter(group=group, user=user).delete()
    await message.reply(f"已删除操作人 @{', @'.join(usernames)}")


async def new_day(message: Message):
    group = await get_group(message)
    if await DailySession.filter(group=group, started_at__gte=message.date.date()).exists():
        raise ReplyAbortError("今日已开始记账")
    await DailySession.create(group=group)
    await reply_bill(
        message,
        f"开始记账 {pendulum.now().to_datetime_string()} - {pendulum.now().start_of('day').add(days=1, hours=4).to_datetime_string()}",
    )


async def set_in_fee_rate(message: Message, rate: Decimal):
    session = await get_daily_session(message)
    session.in_fee_rate = round(rate, 4)
    await session.save()
    await message.reply(f"已设置入款费率为 {session.in_fee_rate.normalize():%}")


async def set_in_exchange_rate(message: Message, rate: Decimal):
    session = await get_daily_session(message)
    session.in_exchange_rate = round(rate, 2)
    await session.save()
    await message.reply(f"已设置入款汇率为 {session.in_exchange_rate.normalize():f}")


async def set_out_fee_rate(message: Message, rate: Decimal):
    session = await get_daily_session(message)
    session.out_fee_rate = round(rate, 4)
    await session.save()
    await message.reply(f"已设置出款费率为 {session.out_fee_rate.normalize():%}")


async def set_out_exchange_rate(message: Message, rate: Decimal):
    session = await get_daily_session(message)
    session.out_exchange_rate = round(rate, 2)
    await session.save()
    await message.reply(f"已设置出款汇率为 {session.out_exchange_rate.normalize():f}")


async def inflow(
    message: Message,
    amount: Decimal,
    fee_rate: Optional[Decimal] = None,
    exchange_rate: Optional[Decimal] = None,
):
    session = await get_daily_session(message)
    await Transaction.create(
        session=session,
        type=Transaction.Type.INCOME,
        currency=Transaction.Currency.CNY,
        amount=amount,
        fee_rate=session.in_fee_rate if fee_rate is None else round(fee_rate, 4),
        exchange_rate=session.in_exchange_rate if exchange_rate is None else round(exchange_rate, 2),
        operator=await get_user(message),
    )
    await reply_bill(message)


async def outflow(
    message: Message,
    amount: Decimal,
    fee_rate: Optional[Decimal] = None,
    exchange_rate: Optional[Decimal] = None,
):
    session = await get_daily_session(message)
    await Transaction.create(
        session=session,
        type=Transaction.Type.PAYOUT,
        currency=Transaction.Currency.CNY,
        amount=amount,
        fee_rate=session.out_fee_rate if fee_rate is None else round(fee_rate, 4),
        exchange_rate=session.out_exchange_rate if exchange_rate is None else round(exchange_rate, 2),
        operator=await get_user(message),
    )
    await reply_bill(message)


async def inflow_correction(
    message: Message, amount: Decimal, fee_rate: Optional[Decimal] = None, exchange_rate: Optional[Decimal] = None
):
    session = await get_daily_session(message)
    await Transaction.create(
        session=session,
        type=Transaction.Type.INCOME,
        currency=Transaction.Currency.CNY,
        amount=amount,
        fee_rate=session.in_fee_rate if fee_rate is None else round(fee_rate, 4),
        exchange_rate=session.in_exchange_rate if exchange_rate is None else round(exchange_rate, 2),
        operator=await get_user(message),
        is_correction=True,
    )
    await reply_bill(message)


async def outflow_correction(
    message: Message,
    amount: Decimal,
    fee_rate: Optional[Decimal] = None,
    exchange_rate: Optional[Decimal] = None,
):
    session = await get_daily_session(message)
    await Transaction.create(
        session=session,
        type=Transaction.Type.PAYOUT,
        currency=Transaction.Currency.CNY,
        amount=amount,
        fee_rate=session.out_fee_rate if fee_rate is None else round(fee_rate, 4),
        exchange_rate=session.out_exchange_rate if exchange_rate is None else round(exchange_rate, 2),
        operator=await get_user(message),
        is_correction=True,
    )
    await reply_bill(message)


async def list_transactions(message: Message):
    session = await get_daily_session(message)
    return await Transaction.filter(session=session)


async def list_inflow(message: Message):
    session = await get_daily_session(message)
    return await Transaction.filter(session=session, type=Transaction.Type.INCOME)


async def list_outflow(message: Message):
    session = await get_daily_session(message)
    return await Transaction.filter(session=session, type=Transaction.Type.PAYOUT)


async def show_bill(message: Message):
    await reply_bill(message)


async def create_full_bill_token(callback_query: CallbackQuery):
    assert callback_query.message and callback_query.message.bot

    group = await get_group(cast(Message, callback_query.message))
    token = await cache.create_token(group.id)
    complete_url = f"{web_settings.url}/bill?token={token}"
    await callback_query.message.bot.send_message(
        callback_query.from_user.id,
        f"点击以下链接查看完整账单:\n{html.link(complete_url, complete_url)}",
    )
    await callback_query.answer("已生成完整账单")
