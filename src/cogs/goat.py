import discord
from discord.ext import commands
import json
import re
from info import *

#for webscraping
from botasaurus import AntiDetectRequests

def fetch_procuct_details(request, arg):
    URL = f"https://ac.cnstrc.com/search/{arg}?c=ciojs-client-2.35.2&key=key_XT7bjdbvjgECO5d8&i=cedf6174-1982-4a30-ad4c-bffe0e7babc0&s=1&page=1&num_results_per_page=24&sort_by=relevance&sort_order=descending&fmt_options%5Bhidden_fields%5D=gp_lowest_price_cents_3&fmt_options%5Bhidden_fields%5D=gp_instant_ship_lowest_price_cents_3&fmt_options%5Bhidden_facets%5D=gp_lowest_price_cents_3&fmt_options%5Bhidden_facets%5D=gp_instant_ship_lowest_price_cents_3&variations_map=%7B%22group_by%22%3A%5B%7B%22name%22%3A%22product_condition%22%2C%22field%22%3A%22data.product_condition%22%7D%2C%7B%22name%22%3A%22box_condition%22%2C%22field%22%3A%22data.box_condition%22%7D%5D%2C%22values%22%3A%7B%22min_regional_price%22%3A%7B%22aggregation%22%3A%22min%22%2C%22field%22%3A%22data.gp_lowest_price_cents_3%22%7D%2C%22min_regional_instant_ship_price%22%3A%7B%22aggregation%22%3A%22min%22%2C%22field%22%3A%22data.gp_instant_ship_lowest_price_cents_3%22%7D%7D%2C%22dtype%22%3A%22object%22%7D&qs=%7B%22features%22%3A%7B%22display_variations%22%3Atrue%7D%2C%22feature_variants%22%3A%7B%22display_variations%22%3A%22matched%22%7D%7D&_dt=1703990333165"
    response = request.get(URL)
    log_info(f"\tFetch Product Detail Status: {response.status_code}")

    if(response.status_code == 200):
        data = response.json()
        try:
            best_match_data = data["response"]["results"][0]
            return best_match_data
        except:
            return None
    return response.status_code

def fetch_market_data(request, slug):
    size_range = [3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 15.5, 16]
    url = "https://sell-api.goat.com/api/v1/analytics/list-variant-availabilities"
    payload = {
        "variant": {
            "id": slug,
            "packaging_condition": 1,
            "region_id": "3"
        }
    }
    response = request.post(url, json=payload)
    log_info(f"\tFetch Market Data Status: {response.status_code}")
    entries = response.json()["availability"]

    market_output = ""
    for entry in entries:
        # Check if the product is new and in the size range
        if(entry["variant"]["product_condition"] != "PRODUCT_CONDITION_NEW"):
            continue
        if(entry["variant"]["size"] not in size_range):
            continue

        try:
            size = str(entry["variant"]["size"])
        except:
            size = "N/A"

        # Market Data
        try:
            lowestAsk = "$" + str(int(entry["lowest_price_cents"]) // 100)
        except:
            lowestAsk = "N/A"
        try:
            highestBid = "$" + str(int(entry["highest_offer_cents"]) // 100)
        except:
            highestBid = "N/A"
        try:
            lastSold = "$" + str(int(entry["last_sold_price_cents"]) // 100)
        except:
            lastSold = "N/A"
        
        market_output += "" + size.ljust(5) + "|" + lowestAsk.ljust(7) + "|" + highestBid.ljust(7) + "|" +lastSold.ljust(7) + "\n"
    return market_output

class goat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def goat(self, ctx, *, arg):
        log_info(f"Goat: {arg}")

        request = AntiDetectRequests(use_stealth=True)
        
        product_details = fetch_procuct_details(request, arg)
        
        if(product_details == None):
            log_info(f"\tProduct Not Found: {arg}")
            product_not_found_embed = discord.Embed(title = arg,
                                                    url = "https://www.goat.com/", 
                                                    color = 0xB702FD)
            product_not_found_embed.add_field(name= "Product Not Found", value="" ,inline=False)
            product_not_found_embed.set_footer(text= "Edwin Z.", icon_url= "https://www.edwinz.dev/img/profile_picture.jpg")
            await ctx.send(embed = product_not_found_embed)
            return 
        
        product_slug = product_details["data"]["slug"]
        product_URL = f"https://www.goat.com/sneakers/{product_slug}"
        product_SKU = product_details["data"]["sku"].replace(" ", "-")
        product_title = product_details["value"]
        product_image = product_details["data"]["image_url"]
        product_retail = "N/A" if product_details["data"]["retail_price_cents"] == 0 else "$" + str(int(product_details["data"]["retail_price_cents"]) // 100)
        log_info(f"\tProduct URL: {product_URL}")
        log_info(f"\tProduct SKU: {product_SKU}")
        log_info(f"\tProduct Title: {product_title}")
        log_info(f"\tProduct Retail: {product_retail}")
        
        market_data = fetch_market_data(request, product_slug)
        market_data_header = "Size |Ask    |Bid    |Sold \n---------------------------\n"
        market_data_embed = discord.Embed(title = product_title,
                                          url   = product_URL, 
                                          color = 0xB702FD)
        market_data_embed.set_thumbnail(url=product_image)

        market_data_embed.add_field(name= "Retail: ", value= product_retail, inline=False)
        market_data_embed.add_field(name= "SKU: ", value= product_SKU, inline=False)
        market_data_embed.add_field(name= "Info", value= "```" + market_data_header + market_data + "```", inline=True)

        market_data_embed.set_footer(text= "Edwin Z.", icon_url= "https://www.edwinz.dev/img/profile_picture.jpg")

        await ctx.send(embed = market_data_embed)

    @commands.command()
    async def goatb(self, ctx, *, arg):
        SKUs = re.split(r';|,|\n| |, | ,', arg)
        log_info(f"Goat BULK: {len(SKUs)} SKUs")

        for SKU in SKUs:
            await self.goat(ctx, arg=SKU)

    #error checking
    @goat.error
    async def goat_error(self, ctx, error):
        await ctx.send(str(error))

#setting up the discord bot for usage
async def setup(bot):
    await bot.add_cog(goat(bot))
    

