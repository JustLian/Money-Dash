from operator import ne
import sys
import traceback
import nextcord
from nextcord.ext import commands
from moneydash import db


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

    @commands.Cog.listener()
    async def on_member_join(self, mem):
        db.create_account(mem.id)


def setup(bot):
    bot.add_cog(Events(bot))
