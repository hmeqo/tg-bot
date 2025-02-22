from decimal import Decimal
from re import Match

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from tortoise.transactions import atomic

from tg_bot.exceptions import ReplyAbortError

from .backend import sdk
from .core import dp
from .decorators import error_handler, require_admin

HELP = """使用手册
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
    '+1000' (入账1000人民币)
    '+1000/7*0.9' (入账1000人民币并设置汇率7.0, 费率10%)
下发:
    '-1000' (下发1000人民币)
    '-1000/7*0.9' (下发1000人民币并设置汇率7.0, 费率10%)
账单:
    显示今日账单, 并显示最近3条数据
"""


@dp.message(Command("test"))
async def test(message: Message):
    assert message.from_user
    await message.reply(f"测试: {message.text}")


@dp.message(Command("help"))
@require_admin
async def help(message: Message):
    await message.reply(HELP)


@dp.message(F.text.regexp(r"^设置操作人((?:\s*@\S+)+)$"))
@atomic()
@require_admin
@error_handler
async def set_operator(message: Message):
    raise ReplyAbortError("暂不支持此功能")


@dp.message(F.text.regexp(r"^开始(记账)?$"))
@atomic()
@require_admin
@error_handler
async def start(message: Message):
    await sdk.new_day(message)


@dp.message(F.text.regexp(r"^设置(?:入款)?费率\s*(\d+(?:\.\d+)?)%?$").as_("match"))
@atomic()
@require_admin
@error_handler
async def set_in_fee_rate(message: Message, match: Match[str]):
    rate = Decimal(match[1]) / 100
    await sdk.set_in_fee_rate(message, rate)


@dp.message(F.text.regexp(r"^设置(?:入款)?汇率\s*(\d+(?:\.\d+)?)$").as_("match"))
@atomic()
@require_admin
@error_handler
async def set_in_exchange_rate(message: Message, match: Match[str]):
    rate = Decimal(match[1])
    await sdk.set_in_exchange_rate(message, rate)


@dp.message(F.text.regexp(r"^设置(?:下发|出款)费率\s*(\d+(?:\.\d+)?)%?$").as_("match"))
@atomic()
@require_admin
@error_handler
async def set_out_fee_rate(message: Message, match: Match[str]):
    rate = Decimal(match[1]) / 100
    await sdk.set_out_fee_rate(message, rate)


@dp.message(F.text.regexp(r"^设置(?:下发|出款)汇率\s*(\d+(?:\.\d+)?)$").as_("match"))
@require_admin
@atomic()
@error_handler
async def set_out_exchange_rate(message: Message, match: Match[str]):
    rate = Decimal(match[1])
    await sdk.set_out_exchange_rate(message, rate)


@dp.message(
    F.text.regexp(r"^\+\s*(\d+(?:\.\d+)?)(?:\s*/\s*(\d+(?:\.\d+)?))?(?:\s*\*\s*(\d+(?:\.\d+)?))?$").as_("match")
)
@atomic()
@require_admin
@error_handler
async def inflow(message: Message, match: Match[str]):
    amount, exchange_rate, fee_rate = match[1], match[2], match[3]
    if exchange_rate is not None:
        exchange_rate = Decimal(exchange_rate)
    if fee_rate is not None:
        fee_rate = 1 - Decimal(fee_rate)
    await sdk.inflow(message, Decimal(amount), fee_rate, exchange_rate)


@dp.message(
    F.text.regexp(r"^\-\s*(\d+(?:\.\d+)?)(?:\s*/\s*(\d+(?:\.\d+)?))?(?:\s*\*\s*(\d+(?:\.\d+)?))?$").as_("match")
)
@atomic()
@require_admin
@error_handler
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
@require_admin
@error_handler
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
@require_admin
@error_handler
async def outflow_correction(message: Message, match: Match[str]):
    amount, exchange_rate, fee_rate = match[1], match[2], match[3]
    if exchange_rate is not None:
        exchange_rate = Decimal(exchange_rate)
    if fee_rate is not None:
        fee_rate = 1 - Decimal(fee_rate)
    await sdk.outflow_correction(message, Decimal(amount), fee_rate, exchange_rate)


@dp.message(F.text.regexp(r"^(?:显示)?账单$"))
@require_admin
@error_handler
async def show_bill(message: Message):
    await sdk.show_bill(message)
