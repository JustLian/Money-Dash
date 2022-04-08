from nextcord import Interaction, SlashOption
import nextcord
import moneydash.db as db
from nextcord.ext import commands
from moneydash import TEST_GUILD_ID


class Main(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @nextcord.slash_command('ping', 'Test if bot is running', [TEST_GUILD_ID])
    async def cmd_ping(self, inter: nextcord.Interaction):
        await inter.response.send_message('Pong!')


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @nextcord.slash_command('profile', 'Получить профиль пользователя', [TEST_GUILD_ID])
    async def cmd_profile(self, inter: Interaction, user: nextcord.User = SlashOption('player', 'Пользователь', required=False)):
        if not user:
            data = db.get_account(inter.user.id)
            em = nextcord.Embed(title='Профиль пользователя',
                                colour=nextcord.Colour.gold())
            if inter.user.avatar is not None:
                em.set_author(name=inter.user.name,
                              icon_url=inter.user.avatar.url)
            else:
                em.set_author(name=inter.user.name)
            em.add_field(name='Наличка', value=data['wallet'])
            em.add_field(name='В банке', value=data['bank'])
            em.add_field(name='Работа', value=(
                lambda: 'Нет' if data['job'] == {} else data['job']['name'])())
            await inter.response.send_message(embed=em)
        else:
            data = db.get_account(user.id)
            em = nextcord.Embed(title='Профиль пользователя',
                                colour=nextcord.Colour.gold())
            if user.avatar is not None:
                em.set_author(name=user.name, icon_url=user.avatar.url)
            else:
                em.set_author(name=user.name)
            em.add_field(name='Наличка', value=data['wallet'])
            em.add_field(name='В банке', value=data['bank'])
            em.add_field(name='Работа', value=(
                lambda: 'Нет' if data['job'] == {} else data['job']['name'])())
            await inter.response.send_message(embed=em)

    @nextcord.slash_command('transfer', 'Перевести деньги пользователю', [TEST_GUILD_ID])
    async def cmd_transfer(self, inter: Interaction, user: nextcord.User = SlashOption('player', 'Пользователь', required=True), amount: int = SlashOption(description='Сумма для перечисления', required=True)):
        data = db.get_account(inter.user.id)
        if data['bank'] >= amount:
            db.update_account(inter.user.id, ('bank', -1 * amount))
            db.update_account(user.id, ('bank', amount))
            em = nextcord.Embed(title='Операция успешна!',
                                colour=nextcord.Colour.green())
            em.add_field(name='В банке', value=data['bank'] - amount)
            await inter.response.send_message(embed=em)
        else:
            em = nextcord.Embed(title='Операция не удалась.',
                                colour=nextcord.Colour.red())
            em.add_field(name='В банке', value=data['bank'])
            await inter.response.send_message(embed=em)

    @nextcord.slash_command('deposit', 'Пополнить баланс в банке', [TEST_GUILD_ID])
    async def cmd_deposit(self, inter: Interaction, amount: int = SlashOption(description='Сумма для пополнения', required=True)):
        data = db.get_account(inter.user.id)
        if data['wallet'] >= amount:
            db.update_account(inter.user.id, ('wallet', -
                              1 * amount), ('bank', amount))
            em = nextcord.Embed(title='Баланс пополнен!',
                                colour=nextcord.Colour.green())
            em.add_field(name='Наличка', value=data['wallet'] - amount)
            em.add_field(name='В банке', value=data['bank'] + amount)
            await inter.response.send_message(embed=em)
        else:
            em = nextcord.Embed(title='Надостаточно налички',
                                colour=nextcord.Colour.red())
            em.add_field(name='Наличка', value=data['wallet'])
            em.add_field(name='В банке', value=data['bank'])
            await inter.response.send_message(embed=em)

    @nextcord.slash_command('withdraw', 'Вывести деньги из банка', [TEST_GUILD_ID])
    async def cmd_withdraw(self, inter: Interaction, amount: int = SlashOption(description='Сумма для вывода', required=True)):
        data = db.get_account(inter.user.id)
        if data['bank'] >= amount:
            db.update_account(
                inter.user.id, ('wallet', amount), ('bank', -1 * amount))
            em = nextcord.Embed(title='Деньги выведены!',
                                colour=nextcord.Colour.green())
            em.add_field(name='Наличка', value=data['wallet'] + amount)
            em.add_field(name='В банке', value=data['bank'] - amount)
            await inter.response.send_message(embed=em)
        else:
            em = nextcord.Embed(
                title='Недостаточно денег в банке', colour=nextcord.Colour.red())
            em.add_field(name='Наличка', value=data['wallet'])
            em.add_field(name='В банке', value=data['bank'])
            await inter.response.send_message(embed=em)


def setup(bot):
    bot.add_cog(Main(bot))
    bot.add_cog(Economy(bot))
