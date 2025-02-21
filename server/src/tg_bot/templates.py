from decimal import Decimal
from typing import Iterable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from backend.api.main.models import *

from .backend import sdk


def detail_transaction(transactions: Iterable[Transaction]):
    lst = []
    for transaction in transactions:
        net_amount = transaction.amount / transaction.exchange_rate * (1 - transaction.fee_rate)
        lst.append(
            f"{transaction.created_at.strftime('%H:%M:%S')}  {transaction.amount.normalize():f}/{transaction.exchange_rate.normalize():f}*{1 - transaction.fee_rate.normalize():f} = {net_amount.normalize():.2f}U"
        )
    return "\n".join(lst)


async def reply_bill(message: Message, text: str | None = None):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="完整账单", callback_data="show_full_bill")],
        ]
    )
    assert message.from_user
    session = await sdk.get_daily_session(message)
    income_list = await sdk.list_inflow(message)
    payout_list = await sdk.list_outflow(message)
    total_income = sum((i.amount for i in income_list), Decimal(0))
    total_payout = sum((i.amount for i in payout_list), Decimal(0))
    total_income_usdt = sum((i.amount / i.exchange_rate * (1 - i.fee_rate) for i in income_list), Decimal(0))
    total_payout_usdt = sum((i.amount / i.exchange_rate * (1 - i.fee_rate) for i in payout_list), Decimal(0))
    remaining_usdt = total_income_usdt - total_payout_usdt

    text = f"""{text or ""}

入款:
{detail_transaction(reversed(income_list[:3])) or "无"}

下发:
{detail_transaction(reversed(payout_list[:3])) or "无"}

今日入款合计: {total_income.normalize():.2f}
今日出款合计: {total_payout.normalize():.2f}

今日入款USDT合计: {total_income_usdt.normalize():.2f}
今日出款USDT合计: {total_payout_usdt.normalize():.2f}
当前剩余USDT合计: {remaining_usdt.normalize():.2f}

入款汇率: {session.in_exchange_rate.normalize():f} 费率: {session.in_fee_rate.normalize():%}
下发汇率: {session.out_exchange_rate.normalize():f} 费率: {session.out_fee_rate.normalize():%}
"""
    await message.reply(text, reply_markup=markup)
