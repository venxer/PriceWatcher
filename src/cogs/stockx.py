import discord
from discord.ext import commands
import json
import random

#for webscraping
import cloudscraper
from bs4 import BeautifulSoup

def fetchProxy():
    with open('../assets/proxies.txt', 'r') as file:
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
    
def fetchProductDetails(arg, proxy):
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
            }
    )
    url = f"https://stockx.com/api/browse?_search={arg}"
    response = scraper.get(url, proxies=proxy)
    data = response.json()

    try:
        bestMatchData = data["Products"][0]
        return bestMatchData
    except:
        return None

def fetchMarketData(data):
    output = ""
    variants = data["variants"]
    # Size, [number of asks]lowestAsk, [past72hrSales]lastSold, [number of bids]highestBid,
    for variant in variants:
        try:
            size = str(variant["traits"]["size"])
        except:
            size = "N/A"
        try:
            numberAsk = str(variant["market"]["state"]["numberOfAsks"])
        except:
            numberAsk = "N/A"
        try:
            lowestAsk = "$" + str(variant["market"]["state"]["lowestAsk"]["amount"])
        except:
            lowestAsk = "N/A"
        try:
            salesLast72Hours = str(variant["market"]["salesInformation"]["salesLast72Hours"])
        except:
            salesLast72Hours = "N/A"
        try:
            lastSold = "$" + str(variant["market"]["salesInformation"]["lastSale"])
        except:
            lastSold = "N/A"
        try:
            numberBids = str(variant["market"]["state"]["numberOfBids"])
        except:
            numberBids = "N/A"
        try:
            highestBid = str("$" + str(variant["market"]["state"]["highestBid"]["amount"]))
        except:
            highestBid = "N/A"

        output += "" + size.ljust(5) + "|" + lowestAsk.ljust(7) + "|" + highestBid.ljust(7) + "|" +lastSold.ljust(7) + "\n"


 
        # output_arr[2] += f"{numberAsk}\n"
        # output_arr[3] += f"${lastSold}\n"
        # output_arr[4] += f"{salesLast72Hours}\n"
        # output_arr[6] += f"{numberBids}\n"

    return output
    
class stockx(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stockx(self, ctx, *, arg):
        try:
            scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'firefox',
                'platform': 'windows',
                'mobile': False
                }
            )
            proxy = fetchProxy()

            productDetails = fetchProductDetails(arg, proxy)
            productURL = "https://stockx.com/" + productDetails["urlKey"]
            productSKU = productDetails["traits"][0]["value"]
            productTitle = productDetails["title"]
            productImage = productDetails["media"]["imageUrl"]
            productRetail = productDetails["retailPrice"]

            response = scraper.get(productURL, proxies=proxy)
            if(response.status_code == 429):
                await ctx.send("Too many Request")
                return
            soup = BeautifulSoup(response.text, 'html.parser')

            content = soup.find("script", {"id":"__NEXT_DATA__"})
            result = json.loads(content.text)
            productData = result["props"]["pageProps"]["req"]["appContext"]["states"]["query"]["value"]["queries"][3]["state"]["data"]["product"]
            productInfo = fetchMarketData(productData)
            
            header = "```Size |Ask    |Bid    |Sold \n---------------------------\n"
            embedMsg = discord.Embed(title = productTitle,
                                    url = productURL, 
                                    color = 0xB702FD)
            embedMsg.set_thumbnail(url=productImage)

            embedMsg.add_field(name= "Retail: ", value= productRetail, inline=False)
            embedMsg.add_field(name= "SKU: ", value= productSKU, inline=False)
            embedMsg.add_field(name= "Info", value= header + productInfo + "```", inline=True)

            # embedMsg.add_field(name= "Size: ", value= productInfo[0], inline=True)
            # embedMsg.add_field(name= "Lowest Ask: ", value= productInfo[1], inline=True)
            # embedMsg.add_field(name= "# of Ask: ", value= productInfo[2], inline=True)

            # embedMsg.add_field(name= "Size: ", value= productInfo[0], inline=True)
            # embedMsg.add_field(name= "Last Sold: ", value= productInfo[3], inline=True)
            # embedMsg.add_field(name= "# Sales 72hr: ", value= productInfo[4], inline=True)

            # embedMsg.add_field(name= "Size: ", value= productInfo[0], inline=True)
            # embedMsg.add_field(name= "Highest Bid: ", value= productInfo[5], inline=True)
            # embedMsg.add_field(name= "# of Bid: ", value= productInfo[6], inline=True)

            embedMsg.set_footer(text= "Edwin Z.", icon_url= "https://www.edwinz.dev/img/profile_picture.jpg")

            await ctx.send(embed = embedMsg)
        except Exception as e:
            await ctx.send(e)
            embedMsg = discord.Embed(title = arg,
                                     url = "https://www.stock.com/", 
                                     color = 0xB702FD)
            embedMsg.add_field(name= "Product Not Found", value="" ,inline=False)
            embedMsg.set_footer(text= "Edwin Z.", icon_url= "https://www.edwinz.dev/img/profile_picture.jpg")
            await ctx.send(embed = embedMsg)

    #error checking
    @stockx.error
    async def stockx_error(self, ctx, error):
        await ctx.send(str(error))

#setting up the discord bot for usage
async def setup(bot):
    await bot.add_cog(stockx(bot))
    

