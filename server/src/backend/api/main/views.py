import csv
import datetime as dt
from io import StringIO
from typing import cast
from urllib.parse import quote

import pendulum
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from .cache import get_group_from_token
from .models import *

api_router = APIRouter(prefix="/api")


@api_router.get("/bill")
async def bill_view(token: str, date: dt.date):
    group = await get_group_from_token(token)
    d = pendulum.instance(dt.datetime.combine(date, dt.time.min)).add(hours=4)
    session = await DailySession.filter(
        group=group,
        started_at__gte=d,
        started_at__lt=d.add(days=1),
    ).last()
    if session is None:
        raise HTTPException(status_code=404, detail="未找到记录")

    transactions = await Transaction.filter(session=session)
    categorized = {
        "inflow_without_correction": [],
        "inflow_with_correction": [],
        "outflow_without_correction": [],
        "outflow_with_correction": [],
        "operators": [],
    }
    if not transactions:
        return categorized
    operators = {}
    for tx in transactions:
        if tx.operator is not None:
            operator = await tx.operator.first()
            if operator.id not in operators:
                operators[operator.id] = operator
        if tx.type == Transaction.Type.INCOME:
            if tx.is_correction:
                categorized["inflow_with_correction"].append(tx)
            else:
                categorized["inflow_without_correction"].append(tx)
        elif tx.type == Transaction.Type.PAYOUT:
            if tx.is_correction:
                categorized["outflow_with_correction"].append(tx)
            else:
                categorized["outflow_without_correction"].append(tx)
    categorized["operators"] = list(operators.values())

    return categorized


@api_router.get("/bill/export")
async def bill_export(token: str):
    group = await get_group_from_token(token)
    session = await DailySession.filter(group=group).last()
    if session is None:
        raise HTTPException(status_code=404, detail="未找到记录")

    transactions = await Transaction.filter(session=session)

    out = StringIO()
    writer = csv.writer(out)
    writer.writerow(["时间", "类型", "币种", "金额", "转换为 USDT", "费率", "汇率", "操作人", "修正"])
    for tx in transactions:
        time = pendulum.instance(cast(dt.datetime, (await tx.session.first()).started_at)).to_iso8601_string()
        amount_usdt = round(tx.amount / tx.exchange_rate * (1 - tx.fee_rate), 2)
        fee_rate = f"{tx.fee_rate:%}"
        username = (await tx.operator.first()).username if tx.operator else ""
        is_correction = "是" if tx.is_correction else "否"
        writer.writerow(
            [
                time,
                tx.type.name,
                tx.currency.name,
                tx.amount,
                amount_usdt,
                fee_rate,
                tx.exchange_rate,
                username,
                is_correction,
            ]
        )
    out.seek(0)
    return StreamingResponse(
        out,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote('完整账单')}.csv"},
    )
