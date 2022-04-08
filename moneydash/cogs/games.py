from nextcord import Interaction, SlashOption
import nextcord
import moneydash.db as db
from nextcord.ext import commands
from moneydash import TEST_GUILD_ID


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command('rob', 'Ограбить игрока - TODO', [TEST_GUILD_ID])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_rob(self, inter: Interaction, user: nextcord.User = SlashOption('player', 'Пользователь', True), amount: int = SlashOption('amount', 'Сумма для ограбления. Выше сумма - меньше шансы на успех', True)):
        await inter.response.send_message('will be implemented in futere')


def setup(bot):
    bot.add_cog(Games(bot))
