import discord
import yaml
from cogs import *
from datetime import datetime
from discord.ext import commands
from torn_client import torn_client


CONFIG_FILE = 'config.yml'


def main():
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    torn = torn_client.TornClient(config['TORN'])
    spam_chan = None


    @bot.event
    async def on_ready():
        spam_chan = next((chan for chan in bot.get_all_channels() if chan.name == config['DISCORD']['SPAM_CHANNEL']), None)

        await bot.add_cog(torn_stocks.TornStocks(bot, spam_chan, torn, config['TORN']))
        await bot.add_cog(torn_items.TornItems(bot, spam_chan, torn, config['TORN']))
        await bot.add_cog(torn_events.TornEvents(bot, spam_chan, torn, config['TORN']))
        await bot.add_cog(torn_market.TornMarket(bot, spam_chan, torn, config['TORN']))

        print(f"{datetime.now()} - spam chan is set to: {spam_chan}")


    @bot.command()
    async def ping(ctx):
        await ctx.channel.typing()
        await ctx.channel.send(f"{ctx.author.mention} PONG!")


    bot.run(config['DISCORD']['BOT_TOKEN'])


if __name__ == '__main__':
    main()