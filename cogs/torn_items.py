from discord.ext import commands


class TornItems(commands.Cog):
    def __init__(self, bot, spam_chan, torn_client, config):
        self.bot = bot
        self.spam_chan = spam_chan
        self.torn_client = torn_client
        self.LISTING_FEE = config['ITEM_MARKET_LISTING_FEE']
        self.config = config

    @commands.command(name="find_profit")
    async def findListingForTargetProfit(self, target_profit:int, purchase_cost:int=0):
        listing = target_profit + purchase_cost
        while(True):
            profit = (listing - (self.LISTING_FEE * listing))
            if (profit < (target_profit + purchase_cost)):
                listing+=1
            else:
                break
        return listing

    # helper method
    # TODO move this into the above command.
    def findNetProfitForlistings(self, listing, purchase_cost, quantity):
        gross = (listing - (self.LISTING_FEE * listing)) * quantity
        return gross - (purchase_cost * quantity)
