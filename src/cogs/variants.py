import discord
from discord.ext import commands
import json
import re
from info import *

from botasaurus import AntiDetectRequests


def align_by_character(strings, char):
    max_index = max(string.find(char) for string in strings if char in string)
    return [string.rjust(max_index + 1) for string in strings]

def format_size_range(size_range):
    lower, upper = map(float, size_range.split("-"))
    
    size_list = [1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,15.5,16,16.5,17,17.5,18,18.5,19,19.5,20]
    size_range_list = []
    for size in size_list:
        if(size >= lower and size <= upper):
            size_range_list.append(size)
            
    return size_range_list

async def fetch_product_info(url):
    request = AntiDetectRequests(use_stealth=True)
    response = request.get(f"{url}.json")

    if(response.status_code == 200):
        product_info = response.json()
        return product_info
    else:
        print(f"Error: {response.status_code}")
        return None
    
def parse_product_info(product_info, size_range):
    size_map = {}
    for variant in product_info["product"]["variants"]:
        if(size_range == "all"):
            size_map[variant["title"]] = variant["id"]
        else:
            if "." in variant["option1"]:
                size = float(re.findall("\d+\.\d+", variant["option1"])[0])
            else:
                size = int(re.findall("\d+", variant["option1"])[0])
    
            if size in size_range:
                size_map[str(size)] = variant["id"]
    log_info(f"Size Formatted")
    return size_map

def getDomain(link):
    log_info(f"Getting Domain")
    try:
        domain = link.split("//")[1:][0].split("/")[0]
        return domain
    except:
        return "Error"

class variants(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def variants(self, ctx, *, arg):
        log_info(f"Variants: {arg}")

        try:
            #all and specific range
            url, inputRange = arg.split(" ")
        except:
            #no range
            url = arg
            inputRange = [1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,15.5,16,16.5,17,17.5,18,18.5,19,19.5,20]

        log_info(f"\tURL: {url}")

        if inputRange == "all":
            log_info(f"\tSize Range: All")
            size_range = "all"
        elif("-" in inputRange):
            log_info(f"\tSize Range: {inputRange}")
            size_range = format_size_range(inputRange)
        else:
            log_info(f"\tSize Range: {inputRange}")
            size_range = inputRange

        product_info = await fetch_product_info(url)
        if(product_info == None):
            log_info(f"\tProduct Info: Not Found")
            await ctx.send("An Error Occurred")
            return
        log_info(f"\tProduct Info: Found")

        sizes = parse_product_info(product_info, size_range)

        makeEmbed = discord.Embed(title="Make", color=0x29ff00)
        makeDescription = ""
        makeEmbed.add_field(name="", value=f"`{getDomain(url)}`", inline=False)

        alpineEmbed = discord.Embed(title="Alpine", color=0x5acaff)
        alpineDescription = "variants:"

        valorEmbed = discord.Embed(title="Valor", color=0xac52ff)
        valorDescription = "var:"

        cyberEmbed = discord.Embed(title="Cyber", color=0x008024)
        cyberDescription = ""

        output = ""
        for(size, id) in sizes.items():
            output += f"{size.ljust(5)} | {id}\n"
            
            makeDescription += f"{id} "
            alpineDescription += f"{id},"
            valorDescription += f"{id},"
            cyberDescription += f"{id},"
            

        makeEmbed.description = f"```{makeDescription.strip()}```"
        alpineEmbed.description = f"```{alpineDescription.strip()[:-1]}```"
        valorEmbed.description = f"```{valorDescription.strip()[:-1]}```"
        cyberEmbed.description = f"```{cyberDescription.strip()[:-1]}```"
        output = f"```{output}```"

        embedList = [makeEmbed, alpineEmbed, valorEmbed, cyberEmbed]
        await ctx.send(output, embeds=embedList)
        
        
    @commands.command()
    async def v(self, ctx, *, arg):
        await self.variants(ctx, arg=arg)

    #error checking
    @variants.error
    async def variants_error(self, ctx, error):
        await ctx.send(str(error))

#setting up the discord bot for usage
async def setup(bot):
    await bot.add_cog(variants(bot))
    

