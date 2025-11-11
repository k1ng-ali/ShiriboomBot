import os
import re
from dataclasses import dataclass

from aiogram.types import Message
from functools import wraps

import asyncio
import pytz
from datetime import datetime, timedelta
from aiogram import Bot

TAJIKISTAN_TZ = pytz.timezone("Asia/Dushanbe")

ADMIN = "ADMIN_ID"

def only_admin(func):
    def decorator(func):
        @wraps(func)
        async def wrapper(msg: Message, *args, **kwargs):
            if str(msg.from_user.id) != ADMIN:
                await msg.answer("⛔ Команда доступна только администратору")
                return
            return await func(msg, *args, **kwargs)
        return wrapper
    return decorator

@dataclass
class AD:
    ad_text:str = os.getenv("AD", "Чати мо: @mmt_taj")

    def set_ad(self, ad_text):
        self.ad_text = ad_text

    def get_ad(self):
        return self.ad_text

    def get_link(self):
        text = self.ad_text.replace("@", "https://t.me/")
        match = re.search(r'(https://\S+|t\.me/\S+)', text)
        ad_link = match.group(0) if match else None
        return ad_link

@dataclass
class DailyStats:
    game_started: int = 0

    def inc_game(self):
        self.game_started += 1

    def get_stats(self) -> str:
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        text = (f"📊 <b>Дневная статистика</b>\n\n"
               f"🎮 Начато игр: {self.game_started}\n"
               f"⏳ Время сбора: {now.date()} {now.strftime('%H:%M')}")
        return text

    def reset_and_dump(self):
        self.game_started = 0

async def send_daily_stats(bot: Bot, stats: DailyStats):
    res = stats.get_stats()
    stats.reset_and_dump()
    await bot.send_message(ADMIN, res, parse_mode="HTML")

async def schedule_daily_stats(bot: Bot, stats: DailyStats):
    while True:
        utc_now = datetime.now(pytz.utc)
        midnight_utc = datetime.combine(utc_now.date(), datetime.min.time(), tzinfo=pytz.utc) + timedelta(days=1)
        seconds = (midnight_utc - utc_now).total_seconds()
        await asyncio.sleep(seconds)
        await send_daily_stats(bot, stats)