import asyncio
import random
import logging

log = logging.getLogger(__name__)

ASSISTANTS = []
ASSISTANT_LOCK = asyncio.Lock()


async def register_assistant(client):
    async with ASSISTANT_LOCK:
        if client not in ASSISTANTS:
            ASSISTANTS.append(client)
            log.info(f"Assistant registered: {client.me.id}")


async def get_random_assistant():
    async with ASSISTANT_LOCK:
        if not ASSISTANTS:
            return None
        return random.choice(ASSISTANTS)
