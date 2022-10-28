from discord.ext import tasks, commands


class TornStocks(commands.Cog):
    def __init__(self, bot, spam_chan, torn_client, config):
        self.bot = bot
        self.spam_chan = spam_chan
        self.torn_client = torn_client
        self.config = config

        self.stocks.start()


    # TODO make this subscribable
    # add bot command to subscribe to
    # checks a users stock transactions and watches current
    # stock prices. spams chat if current price is over
    # specified threshold % from config
    @tasks.loop(seconds=60)
    async def stocks(self):
        profit_percent = self.config['STOCK_PROFIT_PERCENT']

        user_stock_info = await self.user_stocks_info()
        torn_stock_info = await self.torn_stocks_info()

        for stock_id in user_stock_info:
            current_price = torn_stock_info[stock_id]['current_price']
            name = torn_stock_info[stock_id]['name']
            bought_price = user_stock_info[stock_id]['high_price']
            shares = user_stock_info[stock_id]['shares']

            target_sell_price = self.truncate_float(bought_price + (bought_price * profit_percent))
            est_target_profit = (shares * target_sell_price) - (shares * bought_price)
            est_current_profit = (shares * current_price) - (shares * bought_price)


            print(f"CURRENT: {current_price} | BOUGHT: {bought_price} | TARGET: {target_sell_price} | "\
                f"TAR PROF: {self.truncate_float(est_target_profit)} | "\
                f"CUR PROF: {self.truncate_float(est_current_profit)}")
            # If current stock price is at or above profit % price
            if current_price >= target_sell_price:
                await self.spam_chan.typing()
                await self.spam_chan.send(f"@here {name} @ {current_price} SELL SELL!")


    # Returns dict of stock ids mapped ot shares bought and highes price
    # ex: { "8": { "shares": 1234, "high_price": 42.75 } }
    async def user_stocks_info(self, user_id: str="", key: str=""):
        stocks = self.torn_client.getUserStock(user_id, key)
        stock_info = {}
        for stock_id in stocks:
            transactions = stocks[stock_id]['transactions']
            shares = stocks[stock_id]['total_shares']
            highest_bought = 0

            for transaction in transactions:
                bought_price = transactions[transaction]['bought_price']
                highest_bought = highest_bought if highest_bought >= bought_price else bought_price

            stock_info[stock_id] = {
                "shares": shares,
                "high_price": highest_bought
            }

        return stock_info

    # Returns a dict like:
    # "8": {
	# 		"stock_id": 8,
	# 		"name": "Yazoo",
	# 		"acronym": "YAZ",
	# 		"current_price": 41.52,
	# 		"market_cap": 1775703213712,
	# 		"total_shares": 42767418442,
	# 		"investors": 8257
    #      }
    async def torn_stocks_info(self, stock_id: str=""):
        stocks = self.torn_client.getTornStock(stock_id)
        return stocks

    # returns a truncated float at 2 decimals
    def truncate_float(self, number: float):
        split = f"{number}".split('.')
        if len(split) == 1:
            return number
        else:
            split_count = len(split[1])
            if split_count <= 2:
                return number
            else:
                return float(f"{split[0]}.{split[1][:2]}")
