import discord
from discord.ext import commands
import json


#for webscraping
import requests 
from bs4 import BeautifulSoup

class walmart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def walmart(self, ctx, *, arg):
        MAX_COUNT = 10
        count = 0
        existing = []
        URL = f"https://www.walmart.com/search?q={arg}"
        URL = URL.replace(" ", "+")
        print(URL)
        embedMsg = discord.Embed(title = f"Search **Walmart** for **{arg}**",
                            url=URL, color = 0x0071ce) 
        
        Headers = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                   (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})
        response = requests.get(URL, headers=Headers)
        print(f"status: {response.status_code}")
        soup = BeautifulSoup(response.text, 'html.parser')

        next_data_script = soup.find('script', {'id': '__NEXT_DATA__'})
        if next_data_script:
            json_content = json.loads(next_data_script.contents[0])
            item_stacks = json_content["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"]
            items = item_stacks[0].get("items",[])

            print(items)
            for item in items:

                if count > MAX_COUNT:
                    break


                item_name = item.get("name", "N/A")
                item_id = item.get("id", "N/A")
                
                if item_name == "N/A":
                    continue

                # if item_id not in existing:
                existing.append(item_id)                
                priceInfo = item.get("priceInfo")
                item_price = priceInfo.get("linePrice")

                embedMsg.add_field(name = item_name,
                                    value = item_price,
                                    inline = False)
                count += 1



        # # parents = soup.find_all("div", {"role": "group"})
        # parents = soup.find_all("div", {"data-testid": "list-view"})

        # print(len(parents))

        # for parent in parents:
        #     #Need work
        #     # productURL = parent.find("a", {"class": "absolute w-100 h-100 z-1 hide-sibling-opacity"}).get("href")
        #     productName = parent.find("span", {"data-automation-id" : "product-title"}).text
        #     productPrice = parent.find("div", {"data-automation-id" : "product-price"}).find("span", {"class" : "w_iUH7"}).text
        #     embedMsg.add_field(name = productName,
        #                        value = productPrice,
        #                        inline = False)
        #     # print(productPrice)
        #     print(f"{productName} \nPrice: {productPrice}")

        await ctx.send(embed = embedMsg)
    

    #error checking
    @walmart.error
    async def building_search_error(self, ctx, error):
        await ctx.send(str(error))

#setting up the discord bot for usage
async def setup(bot):
    await bot.add_cog(walmart(bot))
    

