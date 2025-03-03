from enum import StrEnum

from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.BigIntField(pk=True)
    chat_id = fields.BigIntField(null=True, description="用户ID")
    username = fields.CharField(max_length=255, null=True, description="用户名")
    joined_at = fields.DatetimeField(auto_now_add=True, description="加入时间")
    is_staff = fields.BooleanField(default=False, description="机器人管理员")

    class Meta:
        table = "tgbot_user"


class Group(Model):
    id = fields.BigIntField(pk=True)
    chat_id = fields.BigIntField(description="群组ID")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "tgbot_group"


class GroupOperator(Model):
    id = fields.BigIntField(pk=True)
    group = fields.ForeignKeyField("models.Group", related_name="operators")
    user = fields.ForeignKeyField("models.User", related_name="groups")
    added_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "tgbot_group_operator"
        unique_together = ("group", "user")


class DailySession(Model):
    id = fields.BigIntField(pk=True)
    group = fields.ForeignKeyField("models.Group", related_name="sessions")
    started_at = fields.DatetimeField(auto_now_add=True, description="开始时间")
    in_fee_rate = fields.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name="费率")
    in_exchange_rate = fields.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name="汇率")
    out_fee_rate = fields.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name="费率")
    out_exchange_rate = fields.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name="汇率")

    class Meta:
        table = "tgbot_daily_session"


class Transaction(Model):
    class Type(StrEnum):
        INCOME = "income"
        PAYOUT = "payout"

        @property
        def name(self):
            match self:
                case self.INCOME:
                    return "入款"
                case self.PAYOUT:
                    return "下发"

    class Currency(StrEnum):
        CNY = "CNY"
        USDT = "USDT"

        @property
        def name(self):
            match self:
                case self.CNY:
                    return "人民币"
                case self.USDT:
                    return "USDT"

    id = fields.BigIntField(pk=True)
    session = fields.ForeignKeyField("models.DailySession", related_name="transactions")
    type = fields.CharEnumField(Type)
    currency = fields.CharEnumField(Currency, default=Currency.CNY)
    amount = fields.DecimalField(max_digits=15, decimal_places=2, description="金额")
    fee_rate = fields.DecimalField(max_digits=10, decimal_places=4, verbose_name="费率")
    exchange_rate = fields.DecimalField(max_digits=10, decimal_places=4, verbose_name="USDT汇率")
    operator = fields.ForeignKeyField("models.User", on_delete=fields.SET_NULL, related_name="transactions", null=True)
    is_correction = fields.BooleanField(default=False, description="修正记录")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "tgbot_transaction"
