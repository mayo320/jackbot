# Introduction
Discord bot invite url: https://discord.com/api/oauth2/authorize?client_id=987846724099911702&permissions=414464862272&scope=bot

Only I can invite it currently

# Usage
## Using the bot
Run **.help** to show list of commands. You can also ping the bot, ie **@jackbot**

## Running the bot
To run the bot:
```
python3 jackbot.py
```

To run it in the background:
```
python3 jackbot.py &
```

To check currently running jobs:
```
jobs
ps -aux | grep jackbot
```

To kill the job:
```
kill <PID>
kill -KILL <PID>
```

Reference: https://kb.iu.edu/d/afnz

# Tech stack
* Python 3.6+
* [Selenium](https://jonathansoma.com/lede/algorithms-2017/servers/setting-up/)
* BeautifulSoup 4
* discord.py
