from discord.ext import tasks, commands

class Stocks(commands.Cog):
    def __init__(self, bot, spam_chan, torn_client, config):
        self.bot = bot
        self.spam_chan = spam_chan
        self.torn_client = torn_client
        self.config = config

        self.stocks.start()

    
    @tasks.loop(seconds=60)
    async def stocks(self):
            stocks = self.torn_client.getStock(id="25")
            current_price = stocks['25']['current_price']
            
            if int(current_price) <= self.config['STOCK_MIN']:
                await self.spam_chan.typing()
                await self.spam_chan.send(f"{current_price} BUY BUY!")
            elif int(current_price) >= self.config['STOCK_MAX']:
                await self.spam_chan.typing()
                await self.spam_chan.send(f"{current_price} SELL SELL!")
            