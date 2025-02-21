from typing import Type

from pydantic import Field
from tortoise.models import Model


async def pk_validator(model: Type[Model], field_name: str, value: int) -> int:
    if not await model.filter(**{field_name: value}).exists():
        raise ValueError(f"{model.__name__} {field_name} {value} 不存在")
    return value
