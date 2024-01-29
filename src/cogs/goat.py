import discord
from discord.ext import commands
import json
import re

#for webscraping
import cloudscraper

def getInfo(productID):
    output = ""
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'firefox',
            'platform': 'windows',
            'mobile': False
        }
    )
    response = scraper.get(f"https://www.goat.com/web-api/v1/product_variants/buy_bar_data?productTemplateId={productID}&countryCode=US")
    result = json.loads(response.text)

    for entry in result:
        if entry["boxCondition"] == "good_condition" and entry["shoeCondition"] == "new_no_defects" and entry != "":
                
            try:
                size = entry["sizeOption"]["value"]
            except KeyError:
                size = "N/A"

            try:
                ask = str(entry["lowestPriceCents"]["amountUsdCents"])
                askString = "$" + str(int(ask) // 100)
            except KeyError:
                askString = "N/A"

            try:
                lastSold = str(entry["lastSoldPriceCents"]["amountUsdCents"])
                lastSoldString = "$" + str(int(lastSold) // 100)
            except KeyError:
                lastSoldString = "N/A"

            output += "" + str(size).ljust(5) + "|" + askString.ljust(10) + "|" + lastSoldString.ljust(9) + "\n"

    return output

class goat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def goat(self, ctx, *, arg):
        scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'firefox',
            'platform': 'windows',
            'mobile': False
            }
        )

        URL = f"https://ac.cnstrc.com/search/{arg}?c=ciojs-client-2.35.2&key=key_XT7bjdbvjgECO5d8&i=cedf6174-1982-4a30-ad4c-bffe0e7babc0&s=1&page=1&num_results_per_page=24&sort_by=relevance&sort_order=descending&fmt_options%5Bhidden_fields%5D=gp_lowest_price_cents_3&fmt_options%5Bhidden_fields%5D=gp_instant_ship_lowest_price_cents_3&fmt_options%5Bhidden_facets%5D=gp_lowest_price_cents_3&fmt_options%5Bhidden_facets%5D=gp_instant_ship_lowest_price_cents_3&variations_map=%7B%22group_by%22%3A%5B%7B%22name%22%3A%22product_condition%22%2C%22field%22%3A%22data.product_condition%22%7D%2C%7B%22name%22%3A%22box_condition%22%2C%22field%22%3A%22data.box_condition%22%7D%5D%2C%22values%22%3A%7B%22min_regional_price%22%3A%7B%22aggregation%22%3A%22min%22%2C%22field%22%3A%22data.gp_lowest_price_cents_3%22%7D%2C%22min_regional_instant_ship_price%22%3A%7B%22aggregation%22%3A%22min%22%2C%22field%22%3A%22data.gp_instant_ship_lowest_price_cents_3%22%7D%7D%2C%22dtype%22%3A%22object%22%7D&qs=%7B%22features%22%3A%7B%22display_variations%22%3Atrue%7D%2C%22feature_variants%22%3A%7B%22display_variations%22%3A%22matched%22%7D%7D&_dt=1703990333165"
        
        response = scraper.get(URL)
        result = json.loads(response.text)

        try:
            topResult = result["response"]["results"][0]

            productID = topResult["data"]["id"]
            productSKU = topResult["data"]["sku"].replace(" ", "-")
            productTitle = topResult["value"]
            productURL = "https://www.goat.com/sneakers/" + topResult["data"]["slug"]
            productImage = topResult["data"]["image_url"]
            productRetail = "N/A" if topResult["data"]["retail_price_cents"] == 0 else "$" + "{:.2f}".format(float(topResult["data"]["retail_price_cents"]) / 100)
            
            header = "```Size " + "|" + "Lowest Ask" + "|" + "Last Sold\n--------------------------\n"
            productInfo = getInfo(productID)

            embedMsg = discord.Embed(title = productTitle,
                                     url = productURL, 
                                     color = 0xB702FD)
            embedMsg.set_thumbnail(url=productImage)
            embedMsg.add_field(name= "Retail: ", value= productRetail, inline=False)
            embedMsg.add_field(name= "SKU: ", value= productSKU, inline=False)
            embedMsg.add_field(name= "Product Info", value= header+productInfo+"```", inline=True)

            embedMsg.set_footer(text= "Edwin Z.", icon_url= "https://www.edwinz.dev/img/profile_picture.jpg")

            await ctx.send(embed = embedMsg)
        
        except:
            embedMsg = discord.Embed(title = arg,
                                     url = "https://www.goat.com/sneakers/", 
                                     color = 0xB702FD)
            embedMsg.add_field(name= "Product Not Found", value="" ,inline=False)
            embedMsg.set_footer(text= "Edwin Z.", icon_url= "https://www.edwinz.dev/img/profile_picture.jpg")
            await ctx.send(embed = embedMsg)

    @commands.command()
    async def goatb(self, ctx, *, arg):
        print("bulk goat")
        SKUs = re.split(r';|,|\n| |, | ,', arg)

        for SKU in SKUs:
            await self.goat(ctx, arg=SKU)

    #error checking
    @goat.error
    async def goat_error(self, ctx, error):
        await ctx.send(str(error))

#setting up the discord bot for usage
async def setup(bot):
    await bot.add_cog(goat(bot))
    

