from discord.ext import commands


class TornItems(commands.Cog):
    def __init__(self, bot, spam_chan, torn_client, config):
        self.bot = bot
        self.spam_chan = spam_chan
        self.torn_client = torn_client
        self.LISTING_FEE = config['ITEM_MARKET_LISTING_FEE']
        self.config = config


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


    @commands.command(name="items")
    async def items(self, ctx):
        items_json = self.torn_client.getTornItems()
        response = items_json['error'] if 'error' in items_json.keys() else items_json['items']['1']['name']
        await ctx.channel.typing()
        await ctx.channel.send(f"{ctx.author.mention} {response}")

    # helper method
    # TODO move this into the above command.
    def findNetProfitForlistings(self, listing, purchase_cost, quantity):
        gross = (listing - (self.LISTING_FEE * listing)) * quantity
        return gross - (purchase_cost * quantity)
