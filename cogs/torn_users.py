from discord.ext import commands


class TornUsers(commands.Cog):
    def __init__(self, bot, spam_chan, torn_client, config):
        self.bot = bot
        self.spam_chan = spam_chan
        self.torn_client = torn_client
        self.config = config

        # { "requestor_id": [{ "user_id": "last_status" }] }
        self.tracked_users = {}


    @commands.command(name="track")
    async def add_track_user(self, ctx):
        r = self.torn_client.getUserStatus()
        await ctx.channel.typing()
        await ctx.channel.send(f"{ctx.author.mention} {r['description']}")


    @tasks.loop(seconds=60)
    async def check_users(self):
        for subscriber_id in self.tracked_users.keys():
            for user_id, status in self.tracked_users[subscriber_id]:
                
