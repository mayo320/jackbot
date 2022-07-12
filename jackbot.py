from lost_crawler import LostCrawler
from parse_html import Merchant, parseMerchants
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
.status         Show current status & active merchants
.history        Show history of cards
```
"""

# Discord tips
# Ping syntax: <@xxx> for user, <@&xxx> for role

class Channel:
    def __init__(self, channel):
        self.ch = channel
        self.pinged_merchants = set()

    async def pingMerchants(self, merchants):
        self._heartbeat()
        roleshash = await self._getRoles()

        for merchant in merchants:
            if merchant.votes < MIN_VOTE:
                continue

            # Ping only if guild has this role
            if merchant.card in roleshash and merchant.card not in self.pinged_merchants:
                embed = discord.Embed(color=0xf1c40f)
                embed.set_image(url=URL + merchant.zone_img)
                await self.ch.send(self._generateMsg(merchant), embed=embed)
                self.pinged_merchants.add(merchant.card)

    def clearMerchants(self):
        self.pinged_merchants.clear()

    async def showStatus(self, merchants):
        self._heartbeat()
        msgs = []
        for merchant in merchants:
            msgs.append(self._generateMsg(merchant))
        if not merchants:
            msgs.append("Waiting for merchants to spawn...")

        embed = discord.Embed()
        embed.title = "Status"
        embed.description = '\n'.join(msgs)
        await self.ch.send(embed=embed)
    
    def _heartbeat(self):
        pass

    async def _getRoles(self):
        roleshash = {} # roles indexed by name
        roles = await self.ch.guild.fetch_roles()
        for role in roles:
            roleshash[role.name] = role
        return roleshash
    
    def _generateMsg(self, merchant):
        return f"{merchant.name} is selling <@&{roleshash[merchant.card].id}> in {merchant.region} - {merchant.zone}"


class MyBot:
    def __init__(self):
        self.crawler = LostCrawler(URL)
        self.client = discord.Client()
        self.channels = {}
        self.merchants = [] # Active merchants
        self.history = []

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
    
    async def _pingAllChannels(self, merchants):
        for cid, ch in self.channels.items():
            await ch.pingMerchants(merchants)

    async def _processHtml(self, html):
        try:
            if "Active Merchants" not in html:
                if self.merchants:
                    self.history.append([])
                    for m in self.merchants:
                        self.history[-1].append(m.card)
                    self.merchants = []

                    if len(self.history) > 20:
                    	self.history.pop(0)
        
                for cid, ch in self.channels.items():
                    ch.clearMerchants()
                return
            
            self.merchants = parseMerchants(html)
            await self._pingAllChannels(self.merchants)

            # for merchant in iterateMerchants(html):
            #     if merchant.votes < MIN_VOTE:
            #         continue

            #     card = merchant.card
            #     if card not in self.found_cards:
            #         try:
            #             await self._pingAllChannels(merchant)
            #             self.found_cards[card] = merchant
            #         except:
            #             print("[ERR] Failed to ping channels for merchant " + merchant.tostring())
        except:
            print("[ERR] Failed to process html\n__________________\n" + html)

    async def _messageHandler(self, message):
        if message.author == self.client.user:
            return
    
        content = message.content
        cid = message.channel.id
        args = content.split(" ")

        if content.startswith(".help") or content.startswith("<@{}>".format(self.client.user.id)):
            await message.channel.send(HELP_TEXT)

        elif content.startswith(".start"):
            if cid not in self.channels:
                self.channels[cid] = Channel(message.channel)
                await message.channel.send("Running on channel \"{}\"".format(message.channel.name))
            else:
                await message.channel.send("Already running on \"{}\"".format(message.channel.name))

        elif content.startswith(".stop"):
            if cid in self.channels:
                del self.channels[cid]
                await message.channel.send("Stopped running on \"{}\"".format(message.channel.name))

        elif content.startswith(".status"):
            if cid in self.channels:
                await self.channels[cid].showStatus(self.merchants)

        elif content.startswith(".history"):
            msg = ""
            for h in self.history:
                msg += ", ".join(h)
                msg += "\n"

            embed = discord.Embed()
            embed.title = "History"
            embed.description = msg
            await message.channel.send(embed=embed)



if __name__ == "__main__":
    bot = MyBot()
    bot.run()