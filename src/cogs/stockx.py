import discord
from discord.ext import commands
import json
import re
import random
from info import *
from uuid import uuid4
import requests

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
    
def fetch_product_details(request, uuid, arg):
    url = "https://stockx.com/api/p/e"
    headers = {
        "Host": "stockx.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:129.0) Gecko/20100101 Firefox/129.0",
        "Accept": "application/json",
        "Accept-Language": "en-US",
        "Referer": "https://stockx.com/",
        "Origin": "https://stockx.com",
        "apollographql-client-name": "Iron",
        "App-Platform": "Iron",
        "App-Version": "2024.09.01.00",
        "x-stockx-device-id": uuid,
        "selected-country": "US",
        "x-operation-name": "GetSearchResults"
    }
    payload = {
        "query": "query GetSearchResults($countryCode: String!, $currencyCode: CurrencyCode!, $filtersVersion: Int, $page: BrowsePageInput, $query: String!, $sort: BrowseSortInput, $flow: BrowseFlow, $ads: BrowseExperimentAdsInput, $staticRanking: BrowseExperimentStaticRankingInput, $list: String, $skipVariants: Boolean!, $market: String, $searchCategoriesDisabled: Boolean!) {\n  browse(\n    query: $query\n    page: $page\n    market: $market\n    flow: $flow\n    sort: $sort\n    filtersVersion: $filtersVersion\n    experiments: {ads: $ads, staticRanking: $staticRanking}\n  ) {\n    categories @skip(if: $searchCategoriesDisabled) {\n      id\n      name\n      count\n    }\n    results {\n      edges {\n        isAd\n        adInventoryType\n        adIdentifier\n        objectId\n        node {\n          ... on Product {\n            id\n            listingType\n            urlKey\n            title\n            primaryTitle\n            secondaryTitle\n            media {\n              thumbUrl\n            }\n            brand\n            productCategory\n            market(currencyCode: $currencyCode) {\n              state(country: $countryCode, market: $market) {\n                askServiceLevels {\n                  expressExpedited {\n                    count\n                    lowest {\n                      amount\n                    }\n                  }\n                  expressStandard {\n                    count\n                    lowest {\n                      amount\n                    }\n                  }\n                }\n              }\n            }\n            favorite(list: $list)\n            variants @skip(if: $skipVariants) {\n              id\n            }\n          }\n          ... on Variant {\n            id\n            product {\n              id\n              listingType\n              urlKey\n              primaryTitle\n              secondaryTitle\n              media {\n                thumbUrl\n              }\n              brand\n              productCategory\n            }\n            market(currencyCode: $currencyCode) {\n              state(country: $countryCode, market: $market) {\n                askServiceLevels {\n                  expressExpedited {\n                    count\n                    lowest {\n                      amount\n                    }\n                  }\n                  expressStandard {\n                    count\n                    lowest {\n                      amount\n                    }\n                  }\n                }\n              }\n            }\n          }\n        }\n      }\n      pageInfo {\n        limit\n        page\n        pageCount\n        queryId\n        queryIndex\n        total\n      }\n    }\n    sort {\n      id\n      order\n    }\n  }\n}",
        "variables": {
            "countryCode": "US",
            "currencyCode": "USD",
            "filtersVersion": 4,
            "query": arg,
            "sort": {
                "id": "featured",
                "order": "DESC"
            },
            "flow": "SEARCH_TYPEAHEAD",
            "ads": {
                "enabled": True
            },
            "staticRanking": {
                "enabled": True
            },
            "skipVariants": True,
            "searchCategoriesDisabled": False,
            "market": "US",
            "page": {
                "index": 1,
                "limit": 10
            }
        },
        "operationName": "GetSearchResults"
    }

    response = request.post(url, headers=headers, json=payload)
    log_info(f"\tFetch Product Detail Status: {response.status_code}")
 
    if(response.status_code == 200):
        data = response.json()
        try:
            best_match_data = data["data"]["browse"]["results"]["edges"][0]["node"]
            return best_match_data
        except:
            return None
    return response.status_code

def fetch_product_data(request, uuid, product_ID):
    url = "https://stockx.com/api/p/e"
    headers = {
            "Host": "stockx.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:129.0) Gecko/20100101 Firefox/129.0",
            "Accept": "application/json",
            "Accept-Language": "en-US",
            "Referer": f'https://stockx.com/{product_ID}',
            "Origin": "https://stockx.com",
            "apollographql-client-name": "Iron",
            "App-Platform": "Iron",
            "App-Version": "2024.09.01.00",
            "x-stockx-device-id": uuid,
            "selected-country": "US",
            'x-operation-name': 'GetProduct',
    }
    payload = {
        "query": "query GetProduct($id: String!, $currencyCode: CurrencyCode, $countryCode: String!, $marketName: String, $skipMerchandising: Boolean!, $skipBreadcrumbs: Boolean!, $verticalImageTestEnabled: Boolean!) {\n  product(id: $id) {\n    id\n    listingType\n    deleted\n    gender\n    browseVerticals\n    ...ProductMerchandisingFragment\n    ...BreadcrumbsFragment\n    ...BreadcrumbSchemaFragment\n    ...HazmatWarningFragment\n    ...HeaderFragment\n    ...NFTHeaderFragment\n    ...MarketActivityFragment\n    ...MediaFragment\n    ...MyPositionFragment\n    ...ProductDetailsFragment\n    ...ProductMetaTagsFragment\n    ...ProductSchemaFragment\n    ...ScreenTrackerFragment\n    ...SizeSelectorWrapperFragment\n    ...StatsForNerdsFragment\n    ...ThreeSixtyImageFragment\n    ...TrackingFragment\n    ...UtilityGroupFragment\n    ...FavoriteProductFragment\n    ...ResellNoFeeFragment\n  }\n}\n\nfragment ProductMerchandisingFragment on Product {\n  id\n  merchandising @skip(if: $skipMerchandising) {\n    title\n    subtitle\n    image {\n      alt\n      url\n    }\n    body\n    trackingEvent\n    link {\n      title\n      url\n      urlType\n    }\n  }\n}\n\nfragment BreadcrumbsFragment on Product {\n  breadcrumbs @skip(if: $skipBreadcrumbs) {\n    name\n    url\n    level\n  }\n  brands {\n    default {\n      alias\n      name\n    }\n  }\n  categories {\n    default {\n      alias\n      value\n      level\n    }\n  }\n}\n\nfragment BreadcrumbSchemaFragment on Product {\n  breadcrumbs @skip(if: $skipBreadcrumbs) {\n    name\n    url\n  }\n  brands {\n    default {\n      alias\n      name\n    }\n  }\n  categories {\n    default {\n      alias\n      value\n      level\n    }\n  }\n}\n\nfragment HazmatWarningFragment on Product {\n  id\n  hazardousMaterial {\n    lithiumIonBucket\n  }\n}\n\nfragment HeaderFragment on Product {\n  primaryTitle\n  secondaryTitle\n  condition\n  productCategory\n}\n\nfragment NFTHeaderFragment on Product {\n  primaryTitle\n  secondaryTitle\n  productCategory\n  editionType\n}\n\nfragment MarketActivityFragment on Product {\n  id\n  title\n  productCategory\n  primaryTitle\n  secondaryTitle\n  media {\n    smallImageUrl\n  }\n}\n\nfragment MediaFragment on Product {\n  id\n  productCategory\n  title\n  brand\n  urlKey\n  variants {\n    id\n    hidden\n    traits {\n      size\n    }\n  }\n  media {\n    gallery\n    imageUrl\n    videos {\n      video {\n        url\n        alt\n      }\n      thumbnail {\n        url\n        alt\n      }\n    }\n    verticalImages @include(if: $verticalImageTestEnabled)\n  }\n}\n\nfragment MyPositionFragment on Product {\n  id\n  urlKey\n}\n\nfragment ProductDetailsFragment on Product {\n  id\n  title\n  productCategory\n  contentGroup\n  browseVerticals\n  description\n  gender\n  traits {\n    name\n    value\n    visible\n    format\n  }\n}\n\nfragment ProductMetaTagsFragment on Product {\n  id\n  urlKey\n  productCategory\n  brand\n  model\n  title\n  description\n  condition\n  styleId\n  breadcrumbs @skip(if: $skipBreadcrumbs) {\n    name\n    url\n  }\n  traits {\n    name\n    value\n  }\n  media {\n    thumbUrl\n    imageUrl\n  }\n  market(currencyCode: $currencyCode) {\n    state(country: $countryCode, market: $marketName) {\n      lowestAsk {\n        amount\n      }\n      numberOfAsks\n    }\n  }\n  variants {\n    id\n    hidden\n    traits {\n      size\n    }\n    market(currencyCode: $currencyCode) {\n      state(country: $countryCode, market: $marketName) {\n        lowestAsk {\n          amount\n        }\n      }\n    }\n  }\n  seo {\n    meta {\n      name\n      value\n    }\n  }\n}\n\nfragment ProductSchemaFragment on Product {\n  id\n  urlKey\n  productCategory\n  brand\n  model\n  title\n  description\n  condition\n  styleId\n  traits {\n    name\n    value\n  }\n  media {\n    thumbUrl\n    imageUrl\n  }\n  market(currencyCode: $currencyCode) {\n    state(country: $countryCode, market: $marketName) {\n      lowestAsk {\n        amount\n      }\n      numberOfAsks\n    }\n  }\n  variants {\n    id\n    hidden\n    traits {\n      size\n    }\n    market(currencyCode: $currencyCode) {\n      state(country: $countryCode, market: $marketName) {\n        lowestAsk {\n          amount\n        }\n      }\n    }\n    gtins {\n      type\n      identifier\n    }\n  }\n}\n\nfragment ScreenTrackerFragment on Product {\n  id\n  brand\n  productCategory\n  primaryCategory\n  title\n  market(currencyCode: $currencyCode) {\n    state(country: $countryCode, market: $marketName) {\n      highestBid {\n        amount\n      }\n      lowestAsk {\n        amount\n      }\n      numberOfAsks\n      numberOfBids\n    }\n    salesInformation {\n      lastSale\n    }\n  }\n  media {\n    imageUrl\n  }\n  traits {\n    name\n    value\n  }\n  variants {\n    id\n    traits {\n      size\n    }\n    market(currencyCode: $currencyCode) {\n      state(country: $countryCode, market: $marketName) {\n        highestBid {\n          amount\n        }\n        lowestAsk {\n          amount\n        }\n        numberOfAsks\n        numberOfBids\n      }\n      salesInformation {\n        lastSale\n      }\n    }\n  }\n  tags\n}\n\nfragment SizeSelectorWrapperFragment on Product {\n  id\n  ...SizeSelectorFragment\n  ...SizeSelectorHeaderFragment\n  ...SizesFragment\n  ...SizesOptionsFragment\n  ...SizeChartFragment\n  ...SizeChartContentFragment\n  ...SizeConversionFragment\n  ...SizesAllButtonFragment\n}\n\nfragment SizeSelectorFragment on Product {\n  id\n  title\n  productCategory\n  browseVerticals\n  sizeDescriptor\n  availableSizeConversions {\n    name\n    type\n  }\n  defaultSizeConversion {\n    name\n    type\n  }\n  variants {\n    id\n    hidden\n    traits {\n      size\n    }\n    sizeChart {\n      baseSize\n      baseType\n      displayOptions {\n        size\n        type\n      }\n    }\n  }\n}\n\nfragment SizeSelectorHeaderFragment on Product {\n  sizeDescriptor\n  productCategory\n  availableSizeConversions {\n    name\n    type\n  }\n}\n\nfragment SizesFragment on Product {\n  id\n  productCategory\n  listingType\n  title\n}\n\nfragment SizesOptionsFragment on Product {\n  id\n  listingType\n  variants {\n    id\n    hidden\n    group {\n      shortCode\n    }\n    traits {\n      size\n    }\n    sizeChart {\n      baseSize\n      baseType\n      displayOptions {\n        size\n        type\n      }\n    }\n    market(currencyCode: $currencyCode) {\n      state(country: $countryCode, market: $marketName) {\n        askServiceLevels {\n          expressExpedited {\n            count\n            lowest {\n              amount\n            }\n          }\n          expressStandard {\n            count\n            lowest {\n              amount\n            }\n          }\n        }\n        lowestAsk {\n          amount\n        }\n      }\n    }\n  }\n}\n\nfragment SizeChartFragment on Product {\n  availableSizeConversions {\n    name\n    type\n  }\n  defaultSizeConversion {\n    name\n    type\n  }\n}\n\nfragment SizeChartContentFragment on Product {\n  availableSizeConversions {\n    name\n    type\n  }\n  defaultSizeConversion {\n    name\n    type\n  }\n  variants {\n    id\n    sizeChart {\n      baseSize\n      baseType\n      displayOptions {\n        size\n        type\n      }\n    }\n  }\n}\n\nfragment SizeConversionFragment on Product {\n  productCategory\n  browseVerticals\n  sizeDescriptor\n  availableSizeConversions {\n    name\n    type\n  }\n  defaultSizeConversion {\n    name\n    type\n  }\n}\n\nfragment SizesAllButtonFragment on Product {\n  id\n  sizeAllDescriptor\n  market(currencyCode: $currencyCode) {\n    state(country: $countryCode, market: $marketName) {\n      lowestAsk {\n        amount\n      }\n      askServiceLevels {\n        expressExpedited {\n          count\n          lowest {\n            amount\n          }\n        }\n        expressStandard {\n          count\n          lowest {\n            amount\n          }\n        }\n      }\n    }\n  }\n}\n\nfragment StatsForNerdsFragment on Product {\n  id\n  title\n  productCategory\n  sizeDescriptor\n  urlKey\n}\n\nfragment ThreeSixtyImageFragment on Product {\n  id\n  title\n  variants {\n    id\n  }\n  productCategory\n  media {\n    all360Images\n  }\n}\n\nfragment TrackingFragment on Product {\n  id\n  productCategory\n  primaryCategory\n  brand\n  title\n  market(currencyCode: $currencyCode) {\n    state(country: $countryCode, market: $marketName) {\n      highestBid {\n        amount\n      }\n      lowestAsk {\n        amount\n      }\n    }\n  }\n  variants {\n    id\n    market(currencyCode: $currencyCode) {\n      state(country: $countryCode, market: $marketName) {\n        highestBid {\n          amount\n        }\n        lowestAsk {\n          amount\n        }\n      }\n    }\n  }\n}\n\nfragment UtilityGroupFragment on Product {\n  id\n  ...PortfolioFragment\n  ...PortfolioContentFragment\n  ...ShareFragment\n}\n\nfragment PortfolioFragment on Product {\n  id\n  title\n  productCategory\n  variants {\n    id\n  }\n  traits {\n    name\n    value\n  }\n}\n\nfragment PortfolioContentFragment on Product {\n  id\n  productCategory\n  sizeDescriptor\n  variants {\n    id\n    traits {\n      size\n    }\n  }\n}\n\nfragment ShareFragment on Product {\n  id\n  productCategory\n  title\n  media {\n    imageUrl\n  }\n}\n\nfragment FavoriteProductFragment on Product {\n  favorite\n}\n\nfragment ResellNoFeeFragment on Product {\n  resellNoFee {\n    enabled\n    eligibilityDays\n  }\n}",
        "variables": {
            "id": product_ID,
            "currencyCode": "USD",
            "countryCode": "US",
            "marketName": "US",
            "skipMerchandising": False,
            "skipBreadcrumbs": False,
            "verticalImageTestEnabled": True
        },
        "operationName": "GetProduct"
    } 
    
    response = request.post(url, headers=headers, json=payload)
    log_info(f"\tFetch Market Data Status: {response.status_code}")
    
    if(response.status_code == 200):
        # print(json.dumps(response.json(), indent=4))
        data = response.json()["data"]["product"]
        product_image = data["media"]["imageUrl"]
        product_SKU = data["traits"][0]["value"]
        product_retail = "$" + str(data["traits"][2]["value"])
        variants = data["variants"]
        market_output, demand_output = fetch_variant_data(variants)
        return data, product_SKU, product_image, product_retail, market_output, demand_output
    if(response.status_code == 403):
        return None, None, None, None, None, None
    
def fetch_variant_data(variants):   
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
    
def blocked_by_cloudflare(arg):
    product_not_found_embed = discord.Embed(title = arg,
                                            url = "https://www.stock.com/", 
                                            color = 0xB702FD)
    product_not_found_embed.add_field(name= "Product Not Found", value="" ,inline=False)
    product_not_found_embed.set_footer(text= "Edwin Z.", icon_url= "https://www.edwinz.dev/img/profile_picture.jpg")
    return product_not_found_embed

class stockx(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stockx(self, ctx, *, arg):
        log_info(f"StockX: {arg}")

        request = AntiDetectRequests(use_stealth=True)
        request.proxies.update(fetch_proxy())

        #generate random uuid
        uuid = str(uuid4())

        product_details = fetch_product_details(request, uuid, arg)

        if(product_details == None):
            log_info(f"\tProduct Not Found: {arg}")
            product_not_found_embed = discord.Embed(title = arg,
                                                    url = "https://www.stock.com/", 
                                                    color = 0xB702FD)
            product_not_found_embed.add_field(name= "Product Not Found", value="" ,inline=False)
            product_not_found_embed.set_footer(text= "Edwin Z.", icon_url= "https://www.edwinz.dev/img/profile_picture.jpg")
            await ctx.send(embed = product_not_found_embed)
            return
        if(product_details == 403):
            log_info(f"\tProduct Not Found: {arg}")
            await ctx.send(embed = blocked_by_cloudflare(arg))
            return
        
        product_ID = product_details["urlKey"]

        product_data, product_SKU, product_image, product_retail, product_market_data, product_demand_data = fetch_product_data(request, uuid, product_details["id"])
        
        if(product_data == None):
            log_info(f"\tProduct Not Found: {arg}")
            await ctx.send(embed = blocked_by_cloudflare(arg))
            return
        
        product_URL = "https://stockx.com/" + product_ID
        product_title = product_details["title"]
        log_info(f"\tProduct URL: {product_URL}")
        log_info(f"\tProduct SKU: {product_SKU}")
        log_info(f"\tProduct Title: {product_title}")
        log_info(f"\tProduct Retail: {product_retail}")

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

    async def stockxb(self, ctx, *, arg):
        SKUs = re.split(r';|,|\n| |, | ,', arg)
        log_info(f"Stockx BULK: {len(SKUs)} SKUs")

        for SKU in SKUs:
            await self.stockx(ctx, arg=SKU)

    #error checking
    @stockx.error
    async def stockx_error(self, ctx, error):
        await ctx.send(str(error))

#setting up the discord bot for usage
async def setup(bot):
    await bot.add_cog(stockx(bot))
    

