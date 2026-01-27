# Authored By Certified Coders © 2025

from pyrogram import filters
from pyrogram.types import Message

from Tune import app
from Tune.misc import SUDOERS
from Tune.utils.database import (
    get_lang,
    is_maintenance,
    maintenance_off,
    maintenance_on,
)
from strings import get_string


@app.on_message(filters.command(["maintenance"]) & SUDOERS)
async def maintenance(client, message: Message):
    try:
        language = await get_lang(message.chat.id)
        _ = get_string(language)
    except:
        _ = get_string("en")

    usage = _["maint_1"]

    if len(message.command) != 2:
        return await message.reply_text(usage)

    state = message.text.split(None, 1)[1].strip().lower()

    if state == "enable":
        # If already enabled
        if await is_maintenance():
            return await message.reply_text(_["maint_4"])
        # Enable maintenance
        await maintenance_on()
        return await message.reply_text(_["maint_2"].format(app.mention))

    elif state == "disable":
        # If already disabled
        if not await is_maintenance():
            return await message.reply_text(_["maint_5"])
        # Disable maintenance
        await maintenance_off()
        return await message.reply_text(_["maint_3"].format(app.mention))

    else:
        return await message.reply_text(usage)
