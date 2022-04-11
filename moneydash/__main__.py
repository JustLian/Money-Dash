from datetime import datetime
import os
import sys
import traceback
import nextcord
from nextcord.ext import commands
import asyncio
from moneydash import TEST_GUILD_ID


with open('./secrets/token', 'r', encoding='utf8') as f:
    _token = f.read().strip()


bot = commands.Bot(command_prefix='-', intents=nextcord.Intents.all())
bot.start_time = datetime.now()


COGS = [name.split('.')[0] for name in os.listdir(
    './moneydash/cogs') if os.path.isfile(os.path.join('./moneydash/cogs', name))]


if __name__ == '__main__':
    for cog in COGS:
        bot.load_extension(f"moneydash.cogs.{cog}")
        print(f"Loaded moneydash.cogs.{cog}")
    bot.run(_token)
