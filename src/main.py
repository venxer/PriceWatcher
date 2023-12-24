import asyncio
import discord
from discord.ext import commands
from bot import Price_Watcher
from info import *

async def main():
    print(f"PREFIX: {PREFIX}")
    print(f"TOKEN: {TOKEN}")

    bot = Price_Watcher(
        prefix = PREFIX,
        intents = discord.Intents.all(),
        token = TOKEN
    )
    await bot.startup()

if __name__ == "__main__":
    asyncio.run(main())

    test