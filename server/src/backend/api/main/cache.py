import secrets

from fastapi import HTTPException

from ..db import redis_client
from .models import Group


async def create_token(group_id: int) -> str:
    # Generate a 64-character hexadecimal string (256 bits).
    # In the unlikely event of a collision, regenerate the token.
    while True:
        token = secrets.token_hex(32)
        key = f":bill:{token}"
        exists = await redis_client.exists(key)
        if not exists:
            break
    # Set expiration to 1 hour (3600 seconds)
    await redis_client.setex(key, 3600, group_id)
    return token


async def get_group_from_token(token: str):
    key = f":bill:{token}"
    group_id = await redis_client.get(key)
    if group_id is None:
        raise HTTPException(status_code=404, detail="无效链接")
    try:
        group_id = int(group_id)
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid group ID")
    group = await Group.get_or_none(id=group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="未找到群组")
    return group
