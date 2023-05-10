from discord.ext import tasks, commands


class TornUsers(commands.Cog):
    def __init__(self, bot, spam_chan, torn_client, config):
        self.bot = bot
        self.spam_chan = spam_chan
        self.torn_client = torn_client
        self.config = config

        # { "subscriber_id": { "user_id": "last_status" } }
        self.tracked_users = {}

        self.check_users.start()


    @commands.command(name="track")
    async def add_track_user(self, ctx, user_id:str = ''):
        # TODO: fix default always tracking rip torn
        r = self.torn_client.getUserStatus(user_id=user_id)
        subscriber = ctx.author

        # TODO: this should be a list of player ids and statuses
        self.tracked_users[subscriber] = { str(r['player_id']): '' }
        await subscriber.send(f"Now tracking {r['name']}")


    @tasks.loop(seconds=60)
    async def check_users(self):
        if len(self.tracked_users.keys()) > 0:
            for subscriber in self.tracked_users.keys():
                # TODO: this should iterate all the tracked statuses for the subscriber
                for user_id, last_status in self.tracked_users[subscriber].items():
                    r = self.torn_client.getUserStatus(user_id=user_id)
                    status = r['status']['description']
                    if status.lower() != last_status.lower():
                        self.tracked_users[subscriber][user_id] = status

                        # dont spam hospital timers
                        if not ("hospital" in last_status.lower() and "hospital" in status.lower()):
                            await subscriber.send(f"{r['name']} is now {status}")
