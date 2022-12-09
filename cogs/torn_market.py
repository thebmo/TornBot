from discord.ext import commands


class TornMarket(commands.Cog):
    def __init__(self, bot, spam_chan, torn_client, config):
        self.bot = bot
        self.spam_chan = spam_chan
        self.torn_client = torn_client
        self.config = config


    # default to getting bear price cause I like beer
    @commands.command(name="price")
    async def getPrice(self, ctx, item_id: str= '180'):
        market_items = self.torn_client.getMarketItem(item_id=item_id)
        high = 0
        low = 999999999

        for item in market_items:
            cost = item['cost']
            high = cost if cost > high else high
            low = cost if cost < low else low

        await ctx.channel.typing()
        await ctx.channel.send(f"{ctx.author.mention} ID: {item_id} | LOW: {low} | HIGH: {high}")