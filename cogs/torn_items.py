from datetime import datetime
from discord.ext import commands


class TornItems(commands.Cog):
    def __init__(self, bot, spam_chan, torn_client, config):
        self.bot = bot
        self.spam_chan = spam_chan
        self.torn_client = torn_client
        self.LISTING_FEE = config['ITEM_MARKET_LISTING_FEE']
        self.config = config
        self.items_cache = {}


    @commands.command(name="find_listing")
    async def findListingForTargetProfit(self, ctx, target_profit:str, purchase_cost:str='0'):
        target_profit = int(target_profit)
        purchase_cost = int(purchase_cost)
        listing = target_profit + purchase_cost

        while(True):
            profit = (listing - (self.LISTING_FEE * listing))
            if (profit < (target_profit + purchase_cost)):
                listing+=1
            else:
                break

        await ctx.channel.typing()
        await ctx.channel.send(f"{ctx.author.mention} {listing}")


    @commands.command(name="item")
    async def item(self, ctx, *args):
        item_name = " ".join(args)
        if len(self.items_cache.keys()) <=0:
            print(f"{datetime.now()} - refreshing items cache")
            await self.refreshTornItems()

        resp_item = {}
        for item_id in self.items_cache:
            item = self.items_cache[item_id]
            if item['name'].lower() == item_name.lower():
                resp_item = item
                resp_item['id'] = item_id
                break

        await ctx.channel.typing()

        if resp_item:
            resp = f"\nNAME: {resp_item['name']}" \
                f"\nID: {resp_item['id']}"
            await ctx.channel.send(f"{ctx.author.mention} {resp}")
        else:
            await ctx.channel.send(f"{ctx.author.mention} {item_name} not found.")


    # helper method
    # TODO move this into the above command.
    def findNetProfitForlistings(self, listing, purchase_cost, quantity):
        gross = (listing - (self.LISTING_FEE * listing)) * quantity
        return gross - (purchase_cost * quantity)


    async def refreshTornItems(self):
        self.items_cache = self.torn_client.getTornItems()['items']
