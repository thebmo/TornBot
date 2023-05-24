from datetime import datetime
from discord.ext import tasks, commands
from re import search


class TornUsers(commands.Cog):
    def __init__(self, bot, spam_chan, torn_client, config):
        self.bot = bot
        self.spam_chan = spam_chan
        self.torn_client = torn_client
        self.config = config

        # { "subscriber(obj)": { "user_id": { "name": "riptorn",  "last_status": "some status" } } }
        self.tracked_users = {}

        self.check_users.start()


    @commands.command(name="track")
    async def add_track_user(self, ctx, user_id:str = ''):
        subscriber = ctx.author
        if self.is_valid_user_id(user_id):
            try:
                r = self.torn_client.getUserStatus(user_id=user_id)
                if r.get('error'):
                    raise Exception(f"{r['error']['error']}")

                # check if subscriber exists, init new dict
                player_id = str(r['player_id'])
                if not self.tracked_users.get(subscriber):
                    self.tracked_users[subscriber] = {}
                self.tracked_users[subscriber][player_id] = { "name": r['name' ], "last_status": '' }

                await subscriber.send(f"Now tracking {r['name']}")
            except Exception as e:
                await subscriber.send(f"I AM ERROR - {e}")
        else:
            await subscriber.send(f"{user_id} is not a valid user id")


    @commands.command(name="untrack")
    async def remove_track_user(self, ctx, user_id:str = ''):
        subscriber = ctx.author
        if not self.is_valid_user_id(user_id):
            await subscriber.send(f"{user_id} is not a valid user id.")
        else:
            try:
                self.tracked_users[subscriber].pop(user_id)
            except KeyError as e:
                print(f"Error removing user id: {user_id}")
            finally:
                await subscriber.send(f"No longer tracking {user_id}")


    @commands.command(name="tracking")
    async def get_tracked_users(self, ctx):
        subscriber = ctx.author
        users = self.tracked_users.get(subscriber)
        msg = "You are not tracking any users"
        if users:
            names = []
            for user_id in users.keys():
                names.append(f"{users[user_id]['name']}({user_id})")

            msg = f"Tracking {', '.join(names)}"

        await subscriber.send(msg)


    # Checks each list of tracked users for each subscriber
    # direct messaging the subscriber with any status
    # changes
    @tasks.loop(seconds=60)
    async def check_users(self):
        if len(self.tracked_users.keys()) > 0:
            for subscriber in self.tracked_users.keys():
                for user_id, user_info in self.tracked_users[subscriber].items():
                    response = None
                    try:
                        response = self.torn_client.getUserStatus(user_id=user_id)
                        if response.get('error'):
                            raise Exception(f"{response['error']['error']}")

                        status = response['status']['description']
                        if status.lower() != user_info['last_status'].lower():
                            self.tracked_users[subscriber][user_id]['last_status'] = status

                            # dont spam hospital timers
                            if not ("hospital" in user_info['last_status'].lower() and "hospital" in status.lower()):
                                await subscriber.send(f"{response['name']} is now {status}")
                    except Exception as e:
                        print(f"{datetime.now()} - Check Users Error - {e}")


    # Helper to check for empty, too short, too long
    # and invalid user Id
    def is_valid_user_id(self, user_id:str):
        user_id = user_id.strip()
        if not user_id or \
            len(user_id) != 7 or \
            search("[a-zA-Z]*\s", user_id):
            return False
        return True
