import discord
from discord.ext import commands
import json
import random
from info import *

#for webscraping
from botasaurus import AntiDetectRequests
from bs4 import BeautifulSoup

class stockx_info_menu(discord.ui.View):
    def __init__(self, pages):
        super().__init__(timeout=120)
        self.pages = pages
        self.current = 0

    @discord.ui.button(label=u"\u25C0", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current == 0:
            self.current = len(self.pages) - 1
        else:
            self.current -= 1
        await interaction.response.edit_message(embed=self.pages[self.current])

    @discord.ui.button(label=u"\u25B6", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current == len(self.pages) - 1:
            self.current = 0
        else:
            self.current += 1
        await interaction.response.edit_message(embed=self.pages[self.current])

def fetch_proxy():
    with open('proxies.txt', 'r') as file:
        proxies = file.readlines()
        proxies = [proxy.strip() for proxy in proxies]

    selectedProxy = random.choice(proxies)

    proxyParts = selectedProxy.split(':')
    proxyURL = f"http://{proxyParts[2]}:{proxyParts[3]}@{proxyParts[0]}:{proxyParts[1]}"

    randomProxy = {
        'http': proxyURL,
        'https': proxyURL,
    }
    return randomProxy
    
def fetch_product_details(request, arg):
    url = f"https://stockx.com/api/browse?_search={arg}"
    response = request.get(url)

    log_info(f"\t Fetch Product Detail Status: {response.status_code}")

    if(response.status_code == 200):
        data = response.json()
        try:
            best_match_data = data["Products"][0]
            return best_match_data
        except:
            return None
    return response.status_code

def fetch_market_data(request, product_URL):
    response = request.get(product_URL)
    log_info(f"\t Fetch Market Data Status: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.find("script", {"id":"__NEXT_DATA__"})
    result = json.loads(content.text)
    variants = result["props"]["pageProps"]["req"]["appContext"]["states"]["query"]["value"]["queries"][3]["state"]["data"]["product"]["variants"]
    market_output = ""
    demand_output = ""

    for variant in variants:
        try:
            size = str(variant["traits"]["size"])
        except:
            size = "N/A"
        
        # Market Data
        try:
            lowestAsk = "$" + str(variant["market"]["state"]["lowestAsk"]["amount"])
        except:
            lowestAsk = "N/A"
        try:
            highestBid = str("$" + str(variant["market"]["state"]["highestBid"]["amount"]))
        except:
            highestBid = "N/A"
        try:
            lastSold = "$" + str(variant["market"]["salesInformation"]["lastSale"])
        except:
            lastSold = "N/A"
        
        # Demand Data
        try:
            numberAsk = str(variant["market"]["state"]["numberOfAsks"])
        except:
            numberAsk = "0"
        try:
            numberBids = str(variant["market"]["state"]["numberOfBids"])
        except:
            numberBids = "0"
        # try:
        #     salesLast72Hours = str(variant["market"]["salesInformation"]["salesLast72Hours"])
        # except:
        #     salesLast72Hours = "0"
        
        market_output += "" + size.ljust(5) + "|" + lowestAsk.ljust(7) + "|" + highestBid.ljust(7) + "|" + lastSold.ljust(7) + "\n"
        demand_output += "" + size.ljust(5) + "|" + numberAsk.ljust(10) + "|" + numberBids.ljust(10) + "\n"

    return market_output, demand_output
    
class stockx(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stockx(self, ctx, *, arg):
        log_info(f"StockX: {arg}")

        request = AntiDetectRequests(use_stealth=True)
        request.proxies.update(fetch_proxy())

        product_details = fetch_product_details(request, arg)

        if(product_details == None):
            log_info(f"\t Product Not Found: {arg}")
            product_not_found_embed = discord.Embed(title = arg,
                                                    url = "https://www.stock.com/", 
                                                    color = 0xB702FD)
            product_not_found_embed.add_field(name= "Product Not Found", value="" ,inline=False)
            product_not_found_embed.set_footer(text= "Edwin Z.", icon_url= "https://www.edwinz.dev/img/profile_picture.jpg")
            await ctx.send(embed = product_not_found_embed)
            return
        if(product_details == 403):
            log_info(f"\t Blocked by Cloudfare: {arg}")
            await ctx.send("Blocked by Cloudfare, try again later.")
            return
        
        product_URL = "https://stockx.com/" + product_details["urlKey"]
        product_SKU = product_details["traits"][0]["value"]
        product_title = product_details["title"]
        product_image = product_details["media"]["imageUrl"]
        product_retail = product_details["retailPrice"]
        log_info(f"\t Product URL: {product_URL}")
        log_info(f"\t Product SKU: {product_SKU}")
        log_info(f"\t Product Title: {product_title}")
        log_info(f"\t Product Retail: {product_retail}")

        product_market_data, product_demand_data = fetch_market_data(request, product_URL)

        pages = []
        page_number = 1

        # Market Data Page
        market_data_header = "Size |Ask    |Bid    |Sold \n---------------------------\n"
        market_data_embed = discord.Embed(title = product_title,
                                          url   = product_URL, 
                                          color = 0xB702FD)
        market_data_embed.set_thumbnail(url=product_image)

        market_data_embed.add_field(name= "Retail: ", value= product_retail, inline=False)
        market_data_embed.add_field(name= "SKU: ", value= product_SKU, inline=False)
        market_data_embed.add_field(name= "Info", value= "```" + market_data_header + product_market_data + "```", inline=False)

        market_data_embed.set_footer(text= "Edwin Z.", icon_url= "https://www.edwinz.dev/img/profile_picture.jpg")

        pages.append(market_data_embed)
        page_number += 1

        # Demand Data Page
        demand_data_header = "Size |# of Ask  |# of Bid  \n---------------------------\n"
        demand_data_embed = discord.Embed(title = product_title,
                                          url   = product_URL, 
                                          color = 0xB702FD)
        demand_data_embed.set_thumbnail(url=product_image)

        demand_data_embed.add_field(name= "Retail: ", value= product_retail, inline=False)
        demand_data_embed.add_field(name= "SKU: ", value= product_SKU, inline=False)
        demand_data_embed.add_field(name= "Info", value= "```" + demand_data_header + product_demand_data + "```", inline=False)

        demand_data_embed.set_footer(text= "Edwin Z.", icon_url= "https://www.edwinz.dev/img/profile_picture.jpg")

        pages.append(demand_data_embed)
        page_number += 1

        view = stockx_info_menu(pages)

        await ctx.send(embed=pages[0], view=view)

    #error checking
    @stockx.error
    async def stockx_error(self, ctx, error):
        await ctx.send(str(error))

#setting up the discord bot for usage
async def setup(bot):
    await bot.add_cog(stockx(bot))
    

