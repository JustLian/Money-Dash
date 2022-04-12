import asyncio
import sys
import traceback
import nextcord
from nextcord.ext import commands
from moneydash import db
from moneydash import __version__ as version


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.reply(embed=nextcord.Embed(title='Команда не найдена', color=nextcord.Colour.dark_orange()))
        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            await ctx.reply(embed=nextcord.Embed(title='Неверное использование команды', description=f"{ctx.prefix}{ctx.command.name} {ctx.command.signature}", color=nextcord.Colour.dark_orange()))
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(embed=nextcord.Embed(title='Команда на задержке', description=f"Попробуй ещё раз через {error.retry_after:.2f} с.", color=nextcord.Colour.dark_orange()))
        else:
            print('Ignoring exception in command {}:'.format(
                ctx.command), file=sys.stderr)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'---\nLogged in as {self.bot.user.name}\n---')
        for guild in self.bot.guilds:
            for member in guild.members:
                if not member.bot:
                    db.create_account(member.id)
        await asyncio.sleep(2)
        await self.bot.change_presence(status=nextcord.Status.idle, activity=nextcord.Activity(
            type=nextcord.ActivityType.playing, name=f"Alpha test ({version})"))
        self.bot.get_cog('Work').loop_work.start()

    @commands.Cog.listener()
    async def on_member_join(self, mem):
        db.create_account(mem.id)


def setup(bot):
    bot.add_cog(Events(bot))
