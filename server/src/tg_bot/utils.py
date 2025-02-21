from aiogram.types import Message


async def is_private(message: Message) -> bool:
    """检查消息是否来自私聊"""
    return message.chat.type == "private"


async def is_group(message: Message) -> bool:
    """检查消息是否来自群组"""
    return message.chat.type == "group"


async def is_chat_admin(message: Message) -> bool:
    """检查消息发送者是否是群组管理员或创建者"""
    assert message.bot and message.from_user

    member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ["creator", "administrator"]
