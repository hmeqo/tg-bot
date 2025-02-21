from aiogram import F
from aiogram.types import CallbackQuery

from .backend import sdk
from .core import dp
from .decorators import error_handler, require_admin


@dp.callback_query(F.data.regexp("^show_full_bill$"))
@require_admin
@error_handler
async def handle_show_full_bill(callback_query: CallbackQuery):
    await sdk.create_full_bill_token(callback_query)
