from discord.ext import tasks, commands


class TornEvents(commands.Cog):
    def __init__(self, bot, spam_chan, torn_client, config):
        self.bot = bot
        self.spam_chan = spam_chan
        self.torn_client = torn_client
        self.config = config
        self.newevents = {}
        self.newevent_cache_length_seconds = 3600 # add to config

        self.clear_newevents.start()
        self.notify_newevents.start()


    @tasks.loop(seconds=60)
    async def notify_newevents(self):
        user_newevents = await self.user_newevents_info()
        newevents_count = 0

        for event_id in user_newevents:
            if not self.newevents.get(event_id, None):
                new_event = user_newevents[event_id]['event']
                self.newevents[event_id] = new_event
                newevents_count += 1

        if newevents_count > 0:
            await self.spam_chan.typing()
            await self.spam_chan.send(f"@here you have {newevents_count} new events.")


    @tasks.loop(seconds=3600)
    async def clear_newevents(self):
        self.newevents = {}


    # Returns dict of user's event ids and messages
    # {
    #     "1001526162": {
    #         "timestamp": 1667075875,
    #         "event": "You were sent some Xanax from
    #           <a href = http://www.torn.com/profiles.php?XID=2086278>KaasChuig</a> 
    #           with the message: Pure sends them to help the faction after all.",
    #         "seen": 0
    #     }
    # }
    async def user_newevents_info(self, user_id: str="", key: str=""):
        return self.torn_client.getUserNewEvents(user_id, key)