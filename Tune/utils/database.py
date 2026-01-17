# Authored By Certified Coders © 2025
# Fixed & Stabilized by ChatGPT (Production Safe)

import random
from typing import Dict, List, Union

from Tune import userbot
from Tune.core.mongo import mongodb

# ================= DATABASES ================= #

authdb = mongodb.adminauth
authuserdb = mongodb.authuser
autoenddb = mongodb.autoend
assdb = mongodb.assistants
blacklist_chatdb = mongodb.blacklistChat
blockeddb = mongodb.blockedusers
chatsdb = mongodb.chats
channeldb = mongodb.cplaymode
countdb = mongodb.upcount
gbansdb = mongodb.gban
langdb = mongodb.language
onoffdb = mongodb.onoffper
playmodedb = mongodb.playmode
playtypedb = mongodb.playtypedb
skipdb = mongodb.skipmode
sudoersdb = mongodb.sudoers
usersdb = mongodb.tgusersdb

# ================= MEMORY CACHE ================= #

active = []
activevideo = []
assistantdict = {}

autoend = {}
count = {}
channelconnect = {}
langm = {}
loop = {}
maintenance = []
nonadmin = {}
pause = {}
playmode = {}
playtype = {}
skipmode = {}
mute = {}

# ================= ASSISTANT CORE ================= #

class NoAssistantAvailable(Exception):
    pass


async def _pick_assistant():
    from Tune.core.userbot import assistants

    if not assistants:
        raise NoAssistantAvailable(
            "No assistant userbots available.\n"
            "Add STRING_SESSION and restart the bot."
        )
    return random.choice(assistants)


async def get_client(assistant: int):
    if int(assistant) == 1:
        return userbot.one
    elif int(assistant) == 2:
        return userbot.two
    elif int(assistant) == 3:
        return userbot.three
    elif int(assistant) == 4:
        return userbot.four
    elif int(assistant) == 5:
        return userbot.five
    return None


async def set_assistant(chat_id: int):
    ran_assistant = await _pick_assistant()

    assistantdict[chat_id] = ran_assistant
    await assdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": ran_assistant}},
        upsert=True,
    )
    return await get_client(ran_assistant)


async def get_assistant(chat_id: int):
    from Tune.core.userbot import assistants

    assistant = assistantdict.get(chat_id)

    if assistant and assistant in assistants:
        return await get_client(assistant)

    dbassistant = await assdb.find_one({"chat_id": chat_id})
    if dbassistant:
        assis = dbassistant.get("assistant")
        if assis in assistants:
            assistantdict[chat_id] = assis
            return await get_client(assis)

    return await set_assistant(chat_id)


async def set_calls_assistant(chat_id: int):
    ran_assistant = await _pick_assistant()

    assistantdict[chat_id] = ran_assistant
    await assdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": ran_assistant}},
        upsert=True,
    )
    return ran_assistant


async def group_assistant(self, chat_id: int):
    from Tune.core.userbot import assistants

    assistant = assistantdict.get(chat_id)

    if not assistant or assistant not in assistants:
        assistant = await set_calls_assistant(chat_id)

    if int(assistant) == 1:
        return self.one
    elif int(assistant) == 2:
        return self.two
    elif int(assistant) == 3:
        return self.three
    elif int(assistant) == 4:
        return self.four
    elif int(assistant) == 5:
        return self.five

# ================= MUSIC / STATES ================= #

async def is_skipmode(chat_id: int) -> bool:
    return skipmode.get(chat_id, True)


async def skip_on(chat_id: int):
    skipmode[chat_id] = True
    await skipdb.delete_one({"chat_id": chat_id})


async def skip_off(chat_id: int):
    skipmode[chat_id] = False
    await skipdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"chat_id": chat_id}},
        upsert=True,
    )


async def is_music_playing(chat_id: int) -> bool:
    return pause.get(chat_id, False)


async def music_on(chat_id: int):
    pause[chat_id] = True


async def music_off(chat_id: int):
    pause[chat_id] = False


async def is_muted(chat_id: int) -> bool:
    return mute.get(chat_id, False)

# ================= ACTIVE CHATS ================= #

async def add_active_chat(chat_id: int):
    if chat_id not in active:
        active.append(chat_id)


async def remove_active_chat(chat_id: int):
    if chat_id in active:
        active.remove(chat_id)


async def is_active_chat(chat_id: int) -> bool:
    return chat_id in active


async def add_active_video_chat(chat_id: int):
    if chat_id not in activevideo:
        activevideo.append(chat_id)


async def remove_active_video_chat(chat_id: int):
    if chat_id in activevideo:
        activevideo.remove(chat_id)


async def is_active_video_chat(chat_id: int) -> bool:
    return chat_id in activevideo

# ================= LANGUAGE / MODE ================= #

async def get_lang(chat_id: int) -> str:
    return langm.get(chat_id, "en")


async def set_lang(chat_id: int, lang: str):
    langm[chat_id] = lang
    await langdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"lang": lang}},
        upsert=True,
    )

# ================= MAINTENANCE ================= #

async def is_maintenance() -> bool:
    data = await onoffdb.find_one({"on_off": 1})
    return bool(data)


async def maintenance_on():
    await onoffdb.update_one(
        {"on_off": 1},
        {"$set": {"on_off": 1}},
        upsert=True,
    )


async def maintenance_off():
    await onoffdb.delete_one({"on_off": 1})

# ================= USERS / BANS ================= #

async def is_served_user(user_id: int) -> bool:
    return bool(await usersdb.find_one({"user_id": user_id}))


async def add_served_user(user_id: int):
    if not await is_served_user(user_id):
        await usersdb.insert_one({"user_id": user_id})


async def is_banned_user(user_id: int) -> bool:
    return bool(await blockeddb.find_one({"user_id": user_id}))


async def add_banned_user(user_id: int):
    if not await is_banned_user(user_id):
        await blockeddb.insert_one({"user_id": user_id})


async def remove_banned_user(user_id: int):
    await blockeddb.delete_one({"user_id": user_id})
