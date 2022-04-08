import asyncio
import random
from nextcord import Interaction, SlashOption
import moneydash.db as db
import nextcord
from nextcord.ext import commands
from moneydash import TEST_GUILD_ID
import moneydash.settings.work as setts
bottles = setts.Bottles


class SelectDist(nextcord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Выберите район",
            max_values=1,
            min_values=1,
            options=[nextcord.SelectOption(
                label=dist) for dist in bottles.dists])
        self.enabled = True

    async def callback(self, inter: Interaction):
        if self.enabled:
            self.enabled = False
            wt = random.randint(5, 7)
            c_bottles = random.randint(*bottles.dists[self.values[0]])
            b_bottles = random.randint(0, 5)

            em = nextcord.Embed(
                title='Начинаю работу!', description=f'Район: {self.values[0]}', colour=nextcord.Colour.brand_green())
            em.add_field(name='Время работы', value=f'{wt}с.')
            em.add_field(name='Ожидаемая зарплата',
                         value=f'{c_bottles * bottles.bottle_cost}')
            await inter.response.edit_message(embed=em, view=None)

            await asyncio.sleep(wt)

            db.update_account(
                inter.user.id, ('wallet', (c_bottles - b_bottles) * bottles.bottle_cost))

            em = nextcord.Embed(
                title='Работа выполнена!', description='Вы сдали все бутылки в приёмный пункт', colour=nextcord.Colour.green())
            em.add_field(name='Собрано бутылок', value=c_bottles)
            em.add_field(name='Разбито бутылок', value=b_bottles)
            em.add_field(name='Доход', value=(
                c_bottles - b_bottles) * bottles.bottle_cost)
            await inter.edit_original_message(embed=em)
        else:
            await inter.response.pong()


class Work(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command('work', 'Начать подработку', [TEST_GUILD_ID])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def cmd_work(self, inter: Interaction, work: str = SlashOption('work', 'Тип работы: [bottles - сбор бутылок;]', True, choices=setts.works)):
        if work == 'bottles':
            view = nextcord.ui.View(timeout=180)
            view.add_item(SelectDist())
            await inter.response.send_message(view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(Work(bot))
