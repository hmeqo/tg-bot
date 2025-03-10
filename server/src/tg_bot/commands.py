import re
from decimal import Decimal
from re import Match

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from tortoise.transactions import atomic

from .backend import sdk
from .core import dp
from .decorators import error_handler, require_admin, require_bot_admin, require_group

README = """README

需将本机器人拉入群组使用, 输入 /help 查看帮助
"""

HELP = """帮助
开始记账输入:
    '开始记账' 或 '开始', 默认到第二天4点结束
设置入款汇率:
    '设置汇率 7.0' (可省略入款)
    '设置入款汇率 7.0'
设置入款费率:
    '设置入款费率 10'
    '设置入款费率 10%'
设置下发汇率:
    '设置下发汇率 7.0'
设置下发费率:
    '设置下发费率 10'
    '设置下发费率 10%'
入款:
    '+1000' - 入账1000人民币
    '+1000/7*0.9' - 入账1000人民币并设置汇率7.0, 费率10%
    '入款-100' - 入款修正
下发:
    '-1000' - 下发1000人民币
    '-1000/7*0.9' - 下发1000人民币并设置汇率7.0, 费率10%
    '下发-100' - 下发修正
账单:
    '显示账单' 或 '账单' 显示今日账单, 并显示最近3条数据
操作人:
    '操作人列表'
    '设置操作人 @xxx'
    '移除操作人 @xxx'
"""


@dp.message(Command("readme"))
async def test(message: Message):
    assert message.from_user
    await message.reply(README)


@dp.message(Command("help"))
@error_handler
@require_admin
@require_group
async def help(message: Message):
    await message.reply(HELP)


@dp.message(Command("broadcast"))
@atomic()
@error_handler
@require_bot_admin
async def broadcast(message: Message):
    await sdk.broadcast_prepare(message)


@dp.message(Command("broadcast_forward"))
@atomic()
@error_handler
@require_bot_admin
async def broadcast_forward(message: Message):
    await sdk.broadcast_forward_prepare(message)


@dp.message(F.text.regexp(r"^操作人列表$"))
@atomic()
@error_handler
@require_admin
@require_group
async def show_operators(message: Message):
    await sdk.list_operators(message)


@dp.message(F.text.regexp(r"^设置操作人((?:\s*@\S+)+)$").as_("match"))
@atomic()
@error_handler
@require_admin
@require_group
async def add_operator(message: Message, match: Match[str]):
    usernames = re.findall(r"@(\S+)", match[1])
    await sdk.add_operator(message, usernames)


@dp.message(F.text.regexp(r"^移除操作人((?:\s*@\S+)+)$").as_("match"))
@atomic()
@error_handler
@require_admin
@require_group
async def remove_operator(message: Message, match: Match[str]):
    usernames = re.findall(r"@(\S+)", match[1])
    await sdk.remove_operator(message, usernames)


@dp.message(F.text.regexp(r"^开始(记账)?$"))
@atomic()
@error_handler
@require_admin
@require_group
async def start(message: Message):
    await sdk.new_day(message)


@dp.message(F.text.regexp(r"^设置(?:入款)?费率\s*(\d+(?:\.\d+)?)%?$").as_("match"))
@atomic()
@error_handler
@require_admin
@require_group
async def set_in_fee_rate(message: Message, match: Match[str]):
    rate = Decimal(match[1]) / 100
    await sdk.set_in_fee_rate(message, rate)


@dp.message(F.text.regexp(r"^设置(?:入款)?汇率\s*(\d+(?:\.\d+)?)$").as_("match"))
@atomic()
@error_handler
@require_admin
@require_group
async def set_in_exchange_rate(message: Message, match: Match[str]):
    rate = Decimal(match[1])
    await sdk.set_in_exchange_rate(message, rate)


@dp.message(F.text.regexp(r"^设置(?:下发|出款)费率\s*(\d+(?:\.\d+)?)%?$").as_("match"))
@atomic()
@error_handler
@require_admin
@require_group
async def set_out_fee_rate(message: Message, match: Match[str]):
    rate = Decimal(match[1]) / 100
    await sdk.set_out_fee_rate(message, rate)


@dp.message(F.text.regexp(r"^设置(?:下发|出款)汇率\s*(\d+(?:\.\d+)?)$").as_("match"))
@atomic()
@error_handler
@require_admin
@require_group
async def set_out_exchange_rate(message: Message, match: Match[str]):
    rate = Decimal(match[1])
    await sdk.set_out_exchange_rate(message, rate)


@dp.message(
    F.text.regexp(r"^\+\s*(\d+(?:\.\d+)?)(?:\s*/\s*(\d+(?:\.\d+)?))?(?:\s*\*\s*(\d+(?:\.\d+)?))?$").as_("match")
)
@atomic()
@error_handler
@require_admin
@require_group
async def inflow(message: Message, match: Match[str]):
    amount, exchange_rate, fee_rate = match[1], match[2], match[3]
    if exchange_rate is not None:
        exchange_rate = Decimal(exchange_rate)
    if fee_rate is not None:
        fee_rate = 1 - Decimal(fee_rate)
    await sdk.inflow(message, Decimal(amount), fee_rate, exchange_rate)


@dp.message(
    F.text.regexp(r"^下发\s*(\d+(?:\.\d+)?)(?:\s*/\s*(\d+(?:\.\d+)?))?(?:\s*\*\s*(\d+(?:\.\d+)?))?$").as_("match")
)
@atomic()
@error_handler
@require_admin
@require_group
async def outflow(message: Message, match: Match[str]):
    amount, exchange_rate, fee_rate = match[1], match[2], match[3]
    if exchange_rate is not None:
        exchange_rate = Decimal(exchange_rate)
    if fee_rate is not None:
        fee_rate = 1 - Decimal(fee_rate)
    await sdk.outflow(message, Decimal(amount), fee_rate, exchange_rate)


@dp.message(
    F.text.regexp(r"^入款([+-]\d+(?:\.\d+)?)(?:\s*/\s*(\d+(?:\.\d+)?))?(?:\s*\*\s*(\d+(?:\.\d+)?))?$").as_("match")
)
@atomic()
@error_handler
@require_admin
@require_group
async def inflow_correction(message: Message, match: Match[str]):
    amount, exchange_rate, fee_rate = match[1], match[2], match[3]
    if exchange_rate is not None:
        exchange_rate = Decimal(exchange_rate)
    if fee_rate is not None:
        fee_rate = 1 - Decimal(fee_rate)
    await sdk.inflow_correction(message, Decimal(amount), fee_rate, exchange_rate)


@dp.message(
    F.text.regexp(r"^下发([+-]\d+(?:\.\d+)?)(?:\s*/\s*(\d+(?:\.\d+)?))?(?:\s*\*\s*(\d+(?:\.\d+)?))?$").as_("match")
)
@atomic()
@error_handler
@require_admin
@require_group
async def outflow_correction(message: Message, match: Match[str]):
    amount, exchange_rate, fee_rate = match[1], match[2], match[3]
    if exchange_rate is not None:
        exchange_rate = Decimal(exchange_rate)
    if fee_rate is not None:
        fee_rate = 1 - Decimal(fee_rate)
    await sdk.outflow_correction(message, Decimal(amount), fee_rate, exchange_rate)


@dp.message(F.text.regexp(r"^(?:显示)?账单$"))
@error_handler
@require_admin
@require_group
async def show_bill(message: Message):
    await sdk.show_bill(message)


@dp.message()
@error_handler
@require_group
async def record(message: Message):
    await sdk.record(message)
