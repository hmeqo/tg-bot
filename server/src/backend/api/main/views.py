import datetime as dt

import pendulum
from fastapi import APIRouter, HTTPException

from .cache import get_group_from_token
from .models import *

api_router = APIRouter(prefix="/api")


@api_router.get("/bill")
async def bill_view(token: str, date: dt.date):
    group = await get_group_from_token(token)
    session = await DailySession.filter(
        group=group,
        start_time__gt=pendulum.instance(dt.datetime.combine(date, dt.time.min)).add(hours=4),
        start_time__lt=pendulum.instance(dt.datetime.combine(date, dt.time.min)).add(days=1, hours=4),
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


@api_router.get("/users/{id}")
async def retrieve_user(id: int):
    user = await User.get_or_none(id=id)
    if user is None:
        raise HTTPException(status_code=404, detail="未找到用户")
    return user
