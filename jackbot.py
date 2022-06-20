from lost_crawler import LostCrawler
from parse_html import Merchant, iterateMerchants
import discord
import asyncio

# Settings
URL = 'https://lostmerchants.com'
TOKEN = open("token.txt").read()
MIN_VOTE = 1
HELP_TEXT = """How can I help you?
```
.help           Show available commands, like this
.start          Bot will ping on this channel
.stop           Stop the bot from pining on this channel
.status         Show current status & re-pinging active merchants
```
"""

# Discord tips
# Ping syntax: <@xxx> for user, <@&xxx> for role

class MyBot:
    def __init__(self):
        self.crawler = LostCrawler(URL)
        self.client = discord.Client()
        self.channels = set()
        self.found_cards = {}
        
    def run(self):
        self._registerEvents()

        async def run():
            f1 = loop.create_task(self.crawler.start())
            f2 = loop.create_task(self.client.start(TOKEN))
            await asyncio.wait([f1, f2])
        async def close():
            f1 = loop.create_task(self.crawler.close())
            f2 = loop.create_task(self.client.close())
            await asyncio.wait([f1, f2])

        loop = asyncio.get_event_loop()
        # loop.run_until_complete(run())
        # loop.close()

        try:
            loop.run_until_complete(run())
        except KeyboardInterrupt:
            loop.run_until_complete(close())
        finally:
            loop.close()

    def _registerEvents(self):
        @self.client.event
        async def on_ready():
            print("User logged in {}".format(self.client.user))

        @self.client.event
        async def on_message(message):
            await self._messageHandler(message)

        async def process_html(html):
            await self._processHtml(html)
        self.crawler.addHandler(process_html)

    def _iterateChannels(self):
        for cid in self.channels:
            ch = self.client.get_channel(cid)
            if ch:
                yield ch

    async def _getRoleByName(self, ch, name):
        roles = await ch.guild.fetch_roles()
        for role in roles:
            if role.name.lower() == name.lower():
                return role
        return None
        
    async def _pingChannel(self, merchant, ch, force=False):
        role_name = merchant.card
        role = await self._getRoleByName(ch, merchant.card)
        if role:
            role_name = "<@&{}>".format(role.id)

        if force or role:
            msg = "{} is selling {} in {} - ".format(merchant.name, role_name, merchant.region)
            msg += "[{}]({})".format(merchant.zone, URL + merchant.zone_img)
            embed = discord.Embed()
            embed.description = msg
            await ch.send(embed=embed)
        
    async def _pingAllChannels(self, merchant):
        for ch in self._iterateChannels():
            await self._pingChannel(merchant, ch)

    async def _broadcast(self, msg):
        for ch in self._iterateChannels():
            await ch.send(msg)

    async def _processHtml(self, html):
        if "Active Merchants" not in html:
            if self.found_cards:
                self.found_cards.clear()
            return
        
        for merchant in iterateMerchants(html):
            if merchant.votes < MIN_VOTE:
                continue

            card = merchant.card
            if card not in self.found_cards:
                await self._pingAllChannels(merchant)
                self.found_cards[card] = merchant

    async def _messageHandler(self, message):
        if message.author == self.client.user:
            return
    
        content = message.content
        args = content.split(" ")

        if content.startswith(".help") or content.startswith("<@{}>".format(self.client.user.id)):
            await message.channel.send(HELP_TEXT)

        elif content.startswith(".start"):
            self.channels.add(message.channel.id)
            await message.channel.send("Running on \"{}\"".format(message.channel.name))

        elif content.startswith(".stop"):
            if message.channel.id in self.channels:
                self.channels.remove(message.channel.id)
                await message.channel.send("Stopped running on \"{}\"".format(message.channel.name))

        elif content.startswith(".status"):
            if self.found_cards:
                for card, merc in self.found_cards.items():
                    await self._pingChannel(merc, message.channel, force=True)
            else:
                await message.channel.send("Waiting for merchants to spawn..")


if __name__ == "__main__":
    bot = MyBot()
    bot.run()