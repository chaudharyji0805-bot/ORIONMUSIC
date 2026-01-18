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
    # ================= CHANNEL MODE ================= #

async def get_cmode(chat_id: int):
    return channelconnect.get(chat_id)


async def set_cmode(chat_id: int, channel_id):
    if channel_id is None:
        channelconnect.pop(chat_id, None)
        await channeldb.delete_one({"chat_id": chat_id})
    else:
        channelconnect[chat_id] = channel_id
        await channeldb.update_one(
            {"chat_id": chat_id},
            {"$set": {"channel_id": channel_id}},
            upsert=True,
        )

# ================= LOOP MODE ================= #

async def get_loop(chat_id: int) -> int:
    return loop.get(chat_id, 0)


async def set_loop(chat_id: int, count: int):
    loop[chat_id] = count
    if count == 0:
        await chatsdb.delete_one({"chat_id": chat_id})
    else:
        await chatsdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"loop": count}},
            upsert=True,
        )

# ================= PLAY MODE (Direct/Inline) ================= #

async def get_playmode(chat_id: int) -> str:
    return playmode.get(chat_id, "Direct")


async def set_playmode(chat_id: int, mode: str):
    playmode[chat_id] = mode
    await playmodedb.update_one(
        {"chat_id": chat_id},
        {"$set": {"mode": mode}},
        upsert=True,
    )

# ================= PLAY TYPE (Everyone/Admin) ================= #

async def get_playtype(chat_id: int) -> str:
    return playtype.get(chat_id, "Everyone")


async def set_playtype(chat_id: int, ptype: str):
    playtype[chat_id] = ptype
    await playtypedb.update_one(
        {"chat_id": chat_id},
        {"$set": {"playtype": ptype}},
        upsert=True,
    )

# ================= UPVOTE / VOTE COUNT ================= #

async def get_upvote_count(chat_id: int) -> int:
    return count.get(chat_id, 2)


async def set_upvotes(chat_id: int, vote_count: int):
    count[chat_id] = vote_count
    await countdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"count": vote_count}},
        upsert=True,
    )

# ================= AUTH USERS ================= #

async def add_authuser(chat_id: int, user_id: int):
    await authuserdb.insert_one({"chat_id": chat_id, "user_id": user_id})


async def remove_authuser(chat_id: int, user_id: int):
    await authuserdb.delete_one({"chat_id": chat_id, "user_id": user_id})


async def get_authuser(chat_id: int):
    authusers = await authuserdb.find({"chat_id": chat_id}).to_list(None)
    return [user["user_id"] for user in authusers] if authusers else []


async def get_authuser_names(chat_id: int):
    authusers = await authuserdb.find({"chat_id": chat_id}).to_list(None)
    return authusers if authusers else []

# ================= NONADMIN CHAT ================= #

async def is_nonadmin_chat(chat_id: int) -> bool:
    return bool(await blacklist_chatdb.find_one({"chat_id": chat_id}))


async def add_nonadmin_chat(chat_id: int):
    if not await is_nonadmin_chat(chat_id):
        await blacklist_chatdb.insert_one({"chat_id": chat_id})


async def remove_nonadmin_chat(chat_id: int):
    await blacklist_chatdb.delete_one({"chat_id": chat_id})

# ================= LOGGING / ON-OFF ================= #

async def is_on_off(chat_id: int) -> bool:
    return bool(await onoffdb.find_one({"chat_id": chat_id}))


async def add_on(chat_id: int):
    await onoffdb.insert_one({"chat_id": chat_id})


async def add_off(chat_id: int):
    await onoffdb.delete_one({"chat_id": chat_id})


async def get_served_chats():
    chats = await chatsdb.find({"chat_id": {"$exists": True}}).to_list(None)
    return [chat["chat_id"] for chat in chats] if chats else []


async def get_banned_count() -> int:
    return await blockeddb.count_documents({})


async def get_banned_users():
    banned = await blockeddb.find({}).to_list(None)
    return [user["user_id"] for user in banned] if banned else []


async def get_gbanned():
    gbans = await gbansdb.find({}).to_list(None)
    return [user["user_id"] for user in gbans] if gbans else []
    
# ================= AUTOEND ================= #

async def is_autoend() -> bool:
    return bool(await autoenddb.find_one({"autoend": 1}))


async def autoend_on():
    await autoenddb.update_one(
        {"autoend": 1},
        {"$set": {"autoend": 1}},
        upsert=True,
    )


async def autoend_off():
    await autoenddb.delete_one({"autoend": 1})


# ================= AUTOEND ================= #

async def is_autoend() -> bool:
    return bool(await autoenddb.find_one({"autoend": 1}))


async def autoend_on():
    await autoenddb.update_one(
        {"autoend": 1},
        {"$set": {"autoend": 1}},
        upsert=True,
    )


async def autoend_off():
    await autoenddb.delete_one({"autoend": 1})


# ================= AUTH USERS ADVANCED ================= #

async def save_authuser(chat_id: int, token: str, data: dict):
    await authuserdb.update_one(
        {"chat_id": chat_id, "token": token},
        {"$set": data},
        upsert=True,
    )


async def delete_authuser(chat_id: int, token: str) -> bool:
    result = await authuserdb.delete_one({"chat_id": chat_id, "token": token})
    return result.deleted_count > 0


async def get_authuser(chat_id: int, token: str):
    return await authuserdb.find_one({"chat_id": chat_id, "token": token})


# ================= ACTIVE CHATS ================= #

async def get_active_chats():
    chats = await chatsdb.find({"chat_id": {"$exists": True}}).to_list(None)
    return chats if chats else []


async def get_served_users():
    users = await usersdb.find({}).to_list(None)
    return users if users else []


# ================= GBAN USERS ================= #

async def add_gban_user(user_id: int):
    if not await is_banned_user(user_id):
        await gbansdb.insert_one({"user_id": user_id})


async def remove_gban_user(user_id: int):
    await gbansdb.delete_one({"user_id": user_id})


# ================= SUDOERS ================= #

async def add_sudo(user_id: int) -> bool:
    sudoersdb = mongodb.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers_list = [] if not sudoers else sudoers.get("sudoers", [])
    
    if user_id not in sudoers_list:
        sudoers_list.append(user_id)
        await sudoersdb.update_one(
            {"sudo": "sudo"},
            {"$set": {"sudoers": sudoers_list}},
            upsert=True,
        )
        return True
    return False


async def remove_sudo(user_id: int) -> bool:
    sudoersdb = mongodb.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers_list = [] if not sudoers else sudoers.get("sudoers", [])
    
    if user_id in sudoers_list:
        sudoers_list.remove(user_id)
        await sudoersdb.update_one(
            {"sudo": "sudo"},
            {"$set": {"sudoers": sudoers_list}},
            upsert=True,
        )
        return True
    return False


async def get_sudoers():
    sudoersdb = mongodb.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    return sudoers.get("sudoers", []) if sudoers else []


# ================= BLACKLIST CHATS ================= #

async def blacklist_chat(chat_id: int):
    blacklistdb = mongodb.blacklistChat
    if not await is_nonadmin_chat(chat_id):
        await blacklistdb.insert_one({"chat_id": chat_id})


async def blacklisted_chats():
    blacklistdb = mongodb.blacklistChat
    chats = await blacklistdb.find({}).to_list(None)
    return [chat["chat_id"] for chat in chats] if chats else []


async def whitelist_chat(chat_id: int):
    blacklistdb = mongodb.blacklistChat
    await blacklistdb.delete_one({"chat_id": chat_id})

# ================= SERVED CHATS ================= #

async def add_served_chat(chat_id: int):
    """Add a chat to the served chats list"""
    if not await is_served_chat(chat_id):
        await chatsdb.insert_one({"chat_id": chat_id})


async def remove_served_chat(chat_id: int):
    """Remove a chat from the served chats list"""
    await chatsdb.delete_one({"chat_id": chat_id})


async def is_served_chat(chat_id: int) -> bool:
    """Check if a chat is served"""
    return bool(await chatsdb.find_one({"chat_id": chat_id}))
