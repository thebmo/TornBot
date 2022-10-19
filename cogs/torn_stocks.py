from discord.ext import tasks, commands


class TornStocks(commands.Cog):
    def __init__(self, bot, spam_chan, torn_client, config):
        self.bot = bot
        self.spam_chan = spam_chan
        self.torn_client = torn_client
        self.config = config
        self.last_known_prices = {}

        self.stocks.start()


    # TODO make this subscribable
    # add bot command to subscribe to
    # add a bit more threshold difference tolerence buy/sell spam
    @tasks.loop(seconds=60)
    async def stocks(self):
        stocks = self.torn_client.getTornStock(id="25")
        current_price = stocks['25']['current_price']
        previous_price = self.last_known_prices.get('25', 0)

        # TODO turn this into proper logging
        print(f"CHECKING STOCKS... previous: {previous_price} | current: {current_price}")

        should_post = current_price != previous_price and previous_price != 0
        if current_price <= self.config['STOCK_MIN'] and should_post:
            await self.spam_chan.typing()
            await self.spam_chan.send(f"@here {current_price} BUY BUY!")
        elif current_price >= self.config['STOCK_MAX'] and should_post:
            await self.spam_chan.typing()
            await self.spam_chan.send(f"@here {current_price} SELL SELL!")

        self.last_known_prices['25'] = current_price
