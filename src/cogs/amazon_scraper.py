import discord
from discord.ext import commands
import asyncio

#for webscraping
import requests 
from bs4 import BeautifulSoup

class amazon_scraper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command (description = 'Searches for buildings in buildings list')
    async def amazon_scraper(self, ctx, *, arg):
        # print("ONLINE")
        await ctx.send(arg)

    #error checking
    @amazon_scraper.error
    async def building_search_error(self, ctx, error):
        await ctx.send(str(error))

#setting up the discord bot for usage
async def setup(bot):
    await bot.add_cog(amazon_scraper(bot))
    