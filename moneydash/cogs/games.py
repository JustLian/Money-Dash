import asyncio
import random
from nextcord import Interaction, SlashOption
import nextcord
import moneydash.db as db
from nextcord.ext import commands
from moneydash import TEST_GUILD_ID
import math


def calc_chance(x):
    N = math.sin(math.atan(x / 180000000))
    if N <= 0.2:
        return math.floor((0.82 - N) * 100)
    return math.floor((1 - N) * 100)


BAL_TYPE = 'bank'


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command('rob', 'Ограбить игрока - TODO', [TEST_GUILD_ID])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_rob(self, inter: Interaction, user: nextcord.User = SlashOption('player', 'Пользователь', True), amount: int = SlashOption('amount', 'Сумма для ограбления. Выше сумма - меньше шансы на успех', True)):
        target = db.get_account(user.id)
        if target[BAL_TYPE] >= amount:
            m = await inter.response.send_message(embed=nextcord.Embed(title='Ограбление', description='Начинаю ограбление...', colour=nextcord.Colour.greyple()))
            await asyncio.sleep(3)
            co = random.randint(85, 100) / 100
            if random.randint(1, 100) <= calc_chance(amount):
                stolen = round(amount * co)
                await inter.edit_original_message(embed=nextcord.Embed(title='Ограбление', description=f'Ограбление удалось! Вам удалось украсть {stolen}!', colour=nextcord.Colour.green()))
                db.update_account(user.id, (BAL_TYPE, -1 * amount))
                db.update_account(inter.user.id, ('wallet', stolen))
            else:
                lost = amount * (1 - co)
                await inter.edit_original_message(embed=nextcord.Embed(title='Ограбление', description=f'Ограбление провалилось! Вы потеряли {lost}', colour=nextcord.Colour.red()))
                db.update_account(inter.user.id, ('wallet', lost))
        else:
            await inter.response.send_message(embed=nextcord.Embed(title='Ограбление', description=f'Недостаточно денег на счету жертвы', colour=nextcord.Colour.brand_red()))


def setup(bot):
    bot.add_cog(Games(bot))
