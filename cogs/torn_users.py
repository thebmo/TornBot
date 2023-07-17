import json
import os
from datetime import datetime
from discord.ext import tasks, commands
from re import search


USERS_FILE = 'tracked_users.json'


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
        # try to Load up stored users if empty
        if self.tracked_users == {}:
            self.tracked_users = await self.load_users()

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
                username = self.tracked_users[subscriber].pop(user_id)["name"]
                await subscriber.send(f"No longer tracking {username}[{user_id}]")
            except KeyError as e:
                print(f"Error removing user id: {user_id}")


    @commands.command(name="tracking")
    async def get_tracked_users(self, ctx):
        subscriber = ctx.author
        users = self.tracked_users.get(subscriber)
        msg = "You are not tracking any users"
        if users:
            names = []
            for user_id in users.keys():
                names.append(f"{users[user_id]['name']}[{user_id}]")

            msg = f"Tracking {', '.join(names)}"

        await subscriber.send(msg)


    # Checks each list of tracked users for each subscriber
    # direct messaging the subscriber with any status
    # changes
    @tasks.loop(seconds=60)
    async def check_users(self):
        # try to Load up stored users if empty
        if self.tracked_users == {}:
            self.tracked_users = await self.load_users()

        if len(self.tracked_users.keys()) > 0:
            for subscriber in self.tracked_users.keys():
                for user_id, user_info in self.tracked_users[subscriber].items():
                    response = None
                    try:
                        response = self.torn_client.getUserStatus(user_id=user_id)
                        if response.get('error'):
                            raise Exception(f"{response['error']['error']}")

                        status = response['status']['description']
                        if self.should_send_message(status, user_info['last_status']):
                            await subscriber.send(f"{response['name']} is now {status}")
                            self.tracked_users[subscriber][user_id]['last_status'] = status
                    except Exception as e:
                        print(f"{datetime.now()} - Check Users Error - {e}")
            self.save_users()


    # Helper to prevent spamming of status updates when in Jail or the Hospital
    def should_send_message(self, status:str, last_status:str):
        instituitions = ["hospital", "jail"]
        status_doesnt_match = status.lower() != last_status.lower()

        already_in_institution = False
        for instituition in instituitions:
            already_in_institution = instituition in last_status.lower() and instituition in status.lower()
            if already_in_institution:
                break

        return status_doesnt_match and not already_in_institution


    # Helper to check for empty, too short, too long
    # and invalid user Id
    def is_valid_user_id(self, user_id:str):
        user_id = user_id.strip()
        if not user_id or \
            len(user_id) != 7 or \
            search("[a-zA-Z]*\s", user_id):
            return False
        return True


    async def load_users(self):
        users = {}
        if os.path.isfile(USERS_FILE) and os.path.getsize(USERS_FILE) > 0:
            temp_users = {}
            with open(USERS_FILE, "r") as f:
                temp_users = json.load(f)
            for id in temp_users.keys():
                user = await self.bot.fetch_user(id)
                # Only load up tracked users for members still
                # in the discord server
                if user:
                    users[user] = temp_users[id]

        return users


    def save_users(self):
        temp_users = {}
        for subscriber in self.tracked_users.keys():
            temp_users[subscriber.id] = self.tracked_users[subscriber]
        with open(USERS_FILE, "w") as f:
            json_object = json.dumps(temp_users, indent=4)
            f.write(json_object)
