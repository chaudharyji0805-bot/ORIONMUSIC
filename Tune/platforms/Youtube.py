import asyncio
import os
import re
import json
import glob
import random
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from Tune.utils.database import is_on_off
from Tune.utils.formatters import time_to_seconds


# =========================
# COOKIES HANDLER
# =========================

def cookie_txt_file():
    folder = f"{os.getcwd()}/cookies"
    files = glob.glob(os.path.join(folder, "*.txt"))
    if not files:
        raise FileNotFoundError("No cookie .txt files found")
    return random.choice(files)


# =========================
# YOUTUBE API CLASS
# =========================

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    # -------------------------
    # URL DETECTION
    # -------------------------
    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message: Message) -> Union[str, None]:
        msgs = [message]
        if message.reply_to_message:
            msgs.append(message.reply_to_message)

        for msg in msgs:
            if msg.entities:
                for e in msg.entities:
                    if e.type == MessageEntityType.URL:
                        text = msg.text or msg.caption
                        return text[e.offset:e.offset + e.length]
        return None

    # -------------------------
    # VIDEO DETAILS
    # -------------------------
    async def details(self, link: str, videoid=False):
        if videoid:
            link = self.base + link
        link = link.split("&")[0]

        search = VideosSearch(link, limit=1)
        result = (await search.next())["result"][0]

        duration_min = result["duration"]
        duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0

        return (
            result["title"],
            duration_min,
            duration_sec,
            result["thumbnails"][0]["url"].split("?")[0],
            result["id"],
        )

    # -------------------------
    # PLAYLIST IDS
    # -------------------------
    async def playlist(self, link, limit, user_id, videoid=False):
        if videoid:
            link = self.listbase + link
        link = link.split("&")[0]

        cmd = (
            f"yt-dlp -i --get-id --flat-playlist "
            f"--cookies {cookie_txt_file()} "
            f"--playlist-end {limit} {link}"
        )

        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, _ = await proc.communicate()
        return [x for x in out.decode().splitlines() if x]

    # =========================
    # DOWNLOAD HANDLER (FIXED)
    # =========================
    async def download(
        self,
        link: str,
        mystic,
        video=False,
        videoid=False,
        songaudio=False,
        songvideo=False,
        format_id=None,
        title=None,
    ):
        if videoid:
            link = self.base + link

        loop = asyncio.get_running_loop()

        # -------------------------
        # AUDIO DOWNLOAD (SAFE)
        # -------------------------
        def audio_dl():
            ydl_opts = {
                # ⛔ HLS BLOCKED HERE
                "format": "bestaudio[protocol!=m3u8]/bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "quiet": True,
                "no_warnings": True,
                "geo_bypass": True,
                "cookiefile": cookie_txt_file(),
                "retries": 3,
                "fragment_retries": 3,
                "skip_unavailable_fragments": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                path = f"downloads/{info['id']}.mp3"

                if os.path.exists(path) and os.path.getsize(path) > 0:
                    return path

                ydl.download([link])

                if not os.path.exists(path) or os.path.getsize(path) == 0:
                    raise Exception("Downloaded audio file is empty")

                return path

        # -------------------------
        # VIDEO DOWNLOAD
        # -------------------------
        def video_dl():
            ydl_opts = {
                "format": "(bestvideo[height<=720][ext=mp4])+(bestaudio[protocol!=m3u8]/bestaudio)",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "quiet": True,
                "no_warnings": True,
                "geo_bypass": True,
                "cookiefile": cookie_txt_file(),
                "merge_output_format": "mp4",
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                path = f"downloads/{info['id']}.mp4"

                if os.path.exists(path) and os.path.getsize(path) > 0:
                    return path

                ydl.download([link])

                if not os.path.exists(path) or os.path.getsize(path) == 0:
                    raise Exception("Downloaded video file is empty")

                return path

        # =========================
        # ROUTER
        # =========================
        if songaudio:
            await loop.run_in_executor(None, audio_dl)
            return f"downloads/{title}.mp3"

        if songvideo:
            await loop.run_in_executor(None, video_dl)
            return f"downloads/{title}.mp4"

        if video:
            if await is_on_off(1):
                return await loop.run_in_executor(None, video_dl), True

            # direct stream fallback
            proc = await asyncio.create_subprocess_exec(
                "yt-dlp",
                "--cookies", cookie_txt_file(),
                "-g",
                "-f",
                "best[height<=720]",
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            out, err = await proc.communicate()
            if out:
                return out.decode().splitlines()[0], False

            return await loop.run_in_executor(None, video_dl), True

        return await loop.run_in_executor(None, audio_dl), True
