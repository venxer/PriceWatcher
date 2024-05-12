import asyncio
import discord

from info import *
from bot import Price_Watcher
from discord.ext import commands

async def main():
    bot = Price_Watcher(
        prefix = PREFIX,
        intents = discord.Intents.all(),
        token = TOKEN
    )
    await bot.startup()

if __name__ == "__main__":
    asyncio.run(main())