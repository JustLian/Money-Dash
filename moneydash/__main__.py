from datetime import datetime
import sys
import traceback
import nextcord
from nextcord.ext import commands
import asyncio
from glob import glob
from moneydash import TEST_GUILD_ID


with open('./secrets/token', 'r', encoding='utf8') as f:
    _token = f.read().strip()


bot = commands.Bot(command_prefix='-', intents=nextcord.Intents.all())
bot.start_time = datetime.now()


COGS = [path.split("\\")[-1][:-3] for path in glob("./moneydash/cogs/*.py")]


if __name__ == '__main__':
    for cog in COGS:
        bot.load_extension(f"moneydash.cogs.{cog}")
        print(f"Loaded moneydash.cogs.{cog}")
    bot.run(_token)
