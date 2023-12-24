import discord
from discord.ext import commands
import asyncio
from info import *

# import requests
# from bs4 import BeautifulSoup

class amazon_scraper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx, *, arg):
        print("pinging")
        print("arg")
        test = arg + "1"
        await ctx.send("pong")

async def setup(bot):
    await bot.add_cog(amazon_scraper(bot))