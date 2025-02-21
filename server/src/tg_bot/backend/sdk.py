from decimal import Decimal
from typing import Optional, cast

import pendulum
from aiogram import html
from aiogram.types import CallbackQuery, Message
from backend.api.main import cache
from backend.api.main.models import *
from project.env import web_settings
from tg_bot.exceptions import ReplyAbortError
from tg_bot.templates import reply_bill


async def get_group(message: Message):
    return (await Group.get_or_create(id=message.chat.id))[0]


async def get_user(message: Message):
    assert message.from_user and message.from_user.username
    user = (await User.get_or_create(id=message.from_user.id))[0]
    if user.username != message.from_user.username:
        user.username = message.from_user.username
        await user.save()
    return user


async def get_daily_session(message: Message):
    group = await get_group(message)
    session = await DailySession.filter(group=group).last()
    if not session or pendulum.instance(session.start_time).end_of("day").add(hours=4) < pendulum.instance(
        message.date
    ).start_of("day"):
        raise ReplyAbortError("请先开始记账")
    return session


async def is_operator(message: Message):
    group = await get_group(message)
    user = await get_user(message)
    return await GroupOperator.filter(group=group, user=user).exists()


async def set_operator_from_entities(message: Message):
    assert message.entities
    # user_ids = []
    for entity in message.entities:
        print(entity.model_dump())
        # assert entity.user
        # print(entity.user.username)
        # user_ids.append(entity.user.id)
    # group = await get_group(message)


async def new_day(message: Message):
    group = await get_group(message)
    if await DailySession.filter(group=group, start_time__gte=message.date.date()).exists():
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
    transaction = await Transaction.create(
        session=session,
        type=Transaction.Type.INCOME,
        currency=Transaction.Currency.CNY,
        amount=amount,
        fee_rate=session.in_fee_rate if fee_rate is None else round(fee_rate, 4),
        exchange_rate=session.in_exchange_rate if exchange_rate is None else round(exchange_rate, 2),
        operator=await get_user(message),
    )
    await message.reply(f"已入账: {transaction.amount.normalize():.2f} CNY")


async def outflow(
    message: Message,
    amount: Decimal,
    fee_rate: Optional[Decimal] = None,
    exchange_rate: Optional[Decimal] = None,
):
    session = await get_daily_session(message)
    transaction = await Transaction.create(
        session=session,
        type=Transaction.Type.PAYOUT,
        currency=Transaction.Currency.CNY,
        amount=amount,
        fee_rate=session.out_fee_rate if fee_rate is None else round(fee_rate, 4),
        exchange_rate=session.out_exchange_rate if exchange_rate is None else round(exchange_rate, 2),
        operator=await get_user(message),
    )
    await message.reply(f"已下发: {transaction.amount.normalize():.2f} CNY")


async def inflow_correction(
    message: Message, amount: Decimal, fee_rate: Optional[Decimal] = None, exchange_rate: Optional[Decimal] = None
):
    session = await get_daily_session(message)
    transaction = await Transaction.create(
        session=session,
        type=Transaction.Type.INCOME,
        currency=Transaction.Currency.CNY,
        amount=amount,
        fee_rate=session.in_fee_rate if fee_rate is None else round(fee_rate, 4),
        exchange_rate=session.in_exchange_rate if exchange_rate is None else round(exchange_rate, 2),
        operator=await get_user(message),
        is_correction=True,
    )
    await message.reply(f"已入账: {transaction.amount.normalize():.2f} CNY")


async def outflow_correction(
    message: Message,
    amount: Decimal,
    fee_rate: Optional[Decimal] = None,
    exchange_rate: Optional[Decimal] = None,
):
    session = await get_daily_session(message)
    transaction = await Transaction.create(
        session=session,
        type=Transaction.Type.PAYOUT,
        currency=Transaction.Currency.CNY,
        amount=amount,
        fee_rate=session.out_fee_rate if fee_rate is None else round(fee_rate, 4),
        exchange_rate=session.out_exchange_rate if exchange_rate is None else round(exchange_rate, 2),
        operator=await get_user(message),
        is_correction=True,
    )
    await message.reply(f"已下发: {transaction.amount.normalize():.2f} CNY")


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
        f"{html.link(complete_url, complete_url)}",
    )
    await callback_query.answer("已生成完整账单")
