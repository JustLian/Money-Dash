import asyncio
import random
from nextcord import Interaction, SlashOption
import moneydash.utils as utils
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

    @nextcord.slash_command('rob', 'Ограбить игрока', [TEST_GUILD_ID])
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

    @nextcord.slash_command('dice', 'Кинуть кости', [TEST_GUILD_ID])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_dice(self, inter: Interaction, amount: int = SlashOption('amount', 'Сумма на которую вы хотите сыграть', True)):
        if db.get_account(inter.user.id)['wallet'] >= amount:
            db.update_account(inter.user.id, ('wallet', -1 * amount))
            file = nextcord.File('./assets/dice.png', filename='dice.png')
            em = nextcord.Embed(
                title='Кости',  description='Бросаю кости...', colour=nextcord.Colour.dark_gold())
            utils.add_author(em, inter.user)
            em.set_thumbnail(url='attachment://dice.png')
            await inter.response.send_message(embed=em, file=file)
            await asyncio.sleep(2)
            k = random.randint(80, 200)
            db.update_account(
                inter.user.id, ('wallet', round(amount * (k / 100))))
            em.description = f'Вы выиграли {round(amount * (k / 100))}!'
            if k >= 100:
                em.colour = nextcord.Colour.gold()
            else:
                em.colour = nextcord.Colour.blurple()
            file = nextcord.File('./assets/dice.png', filename='dice.png')
            await inter.edit_original_message(embed=em, file=file)
        else:
            data = db.get_account(inter.user.id)
            em = nextcord.Embed(title='Надостаточно налички',
                                colour=nextcord.Colour.red())
            em.add_field(name='Наличка', value=data['wallet'])
            em.add_field(name='В банке', value=data['bank'])
            await inter.response.send_message(embed=em)

    @nextcord.slash_command('coin_flip', 'Бросить монету', [TEST_GUILD_ID])
    @commands.cooldown(1, 8, commands.BucketType.user)
    async def cmd_coinflip(self, inter: Interaction, amount: int = SlashOption('amount', 'Сумма на которую вы хотите сыграть', True)):
        if db.get_account(inter.user.id)['wallet'] >= amount:
            em = nextcord.Embed(
                title='Подкидываю монету', description=f'Вы поставили {amount}', colour=nextcord.Colour.dark_gold())
            await inter.response.send_message(embed=em)
            await asyncio.sleep(3)
            if random.randint(0, 1) == 1:
                em.description = f'Вы выиграли {amount * 1.5}!'
                em.colour = nextcord.Colour.gold()
                await inter.edit_original_message(embed=em)
                db.update_account(inter.user.id, ('wallet', amount * 1.5))
            else:
                em.description = f'Вы проиграли!'
                em.colour = nextcord.Colour.dark_blue()
                await inter.edit_original_message(embed=em)
                db.update_account(inter.user.id, ('wallet', -1 * amount))
        else:
            data = db.get_account(inter.user.id)
            em = nextcord.Embed(title='Надостаточно налички',
                                colour=nextcord.Colour.red())
            em.add_field(name='Наличка', value=data['wallet'])
            em.add_field(name='В банке', value=data['bank'])
            await inter.response.send_message(embed=em)


def setup(bot):
    bot.add_cog(Games(bot))
