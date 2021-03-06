# Introduction
Discord bot invite url: https://discord.com/api/oauth2/authorize?client_id=987846724099911702&permissions=414464862272&scope=bot

Only I can invite it currently

# Usage
## Using the bot
Run **.help** to show list of commands. You can also ping the bot, ie **@jackbot**

## Running the bot
* In **lost_crawler.py**, set **CHROME_PATH** to correct path.
* Create a file called **token.txt** that contains your discord bot token

To run the bot
```
python3 jackbot.py
```

To run it in the background and keep it running while logged out
```
nohup python3 -u jackbot.py &
```

To check currently running jobs
```
jobs
ps -aux | grep jackbot
```

To kill the job
```
kill <PID>
pkill chorme
```

Reference: https://kb.iu.edu/d/afnz

# Tech stack
* Python 3.6+
* [Selenium](https://jonathansoma.com/lede/algorithms-2017/servers/setting-up/)
* BeautifulSoup 4
* discord.py
