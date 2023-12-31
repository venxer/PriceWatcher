import discord
from discord.ext import commands
import json

#for webscraping
import requests 
import cloudscraper

from bs4 import BeautifulSoup

def getInfo(productID):
    scraper = cloudscraper.create_scraper()

    URL = f"https://www.goat.com/web-api/v1/product_variants/buy_bar_data?productTemplateId={productID}&countryCode=US"
    scraper = cloudscraper.create_scraper()
    response = scraper.get(URL)
    result = json.loads(response.text)

    return(result)

class goat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


        
    @commands.command()
    async def goat(self, ctx, *, arg):
        scraper = cloudscraper.create_scraper()

        URL = f"https://ac.cnstrc.com/search/{arg}?c=ciojs-client-2.35.2&key=key_XT7bjdbvjgECO5d8&i=cedf6174-1982-4a30-ad4c-bffe0e7babc0&s=1&page=1&num_results_per_page=24&sort_by=relevance&sort_order=descending&fmt_options%5Bhidden_fields%5D=gp_lowest_price_cents_3&fmt_options%5Bhidden_fields%5D=gp_instant_ship_lowest_price_cents_3&fmt_options%5Bhidden_facets%5D=gp_lowest_price_cents_3&fmt_options%5Bhidden_facets%5D=gp_instant_ship_lowest_price_cents_3&variations_map=%7B%22group_by%22%3A%5B%7B%22name%22%3A%22product_condition%22%2C%22field%22%3A%22data.product_condition%22%7D%2C%7B%22name%22%3A%22box_condition%22%2C%22field%22%3A%22data.box_condition%22%7D%5D%2C%22values%22%3A%7B%22min_regional_price%22%3A%7B%22aggregation%22%3A%22min%22%2C%22field%22%3A%22data.gp_lowest_price_cents_3%22%7D%2C%22min_regional_instant_ship_price%22%3A%7B%22aggregation%22%3A%22min%22%2C%22field%22%3A%22data.gp_instant_ship_lowest_price_cents_3%22%7D%7D%2C%22dtype%22%3A%22object%22%7D&qs=%7B%22features%22%3A%7B%22display_variations%22%3Atrue%7D%2C%22feature_variants%22%3A%7B%22display_variations%22%3A%22matched%22%7D%7D&_dt=1703990333165"
        print(URL)
        embedMsg = discord.Embed(title = f"Search **Goat** for **{arg}**",
                            url=URL, color = 0x0071ce) 
        
        # Headers ={'accept': '*/*',
        #           'accept-encoding': 'gzip, deflate, br',
        #           'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        #           'dnt': '1',
        #           'origin': 'https://www.goat.com',
        #           'sec-fetch-dest': 'empty',
        #           'sec-fetch-mode': 'cors',
        #           'sec-fetch-site': 'cross-site',
        #           'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
        # response = requests.get(URL, headers=Headers)
        response = scraper.get(URL)
        result = json.loads(response.text)

        # try:
        topResult = result["response"]["results"][0]
        productID = topResult["data"]["id"]
        productTitle = topResult["value"]
        productURL = "https://www.goat.com/sneakers/" + topResult["data"]["slug"]
        
        test = getInfo("test")
        print(test)
        
        await ctx.send(productTitle)
        await ctx.send(productURL)
        # except:
        await ctx.send("Product Not Found")

        # await ctx.send(embed = embedMsg)
    

    #error checking
    @goat.error
    async def building_search_error(self, ctx, error):
        await ctx.send(str(error))

#setting up the discord bot for usage
async def setup(bot):
    await bot.add_cog(goat(bot))
    

