import asyncio
import random
from nextcord import Interaction, SlashOption
import moneydash.db as db
import nextcord
import moneydash.utils as utils
from nextcord.ext import commands, tasks
from moneydash import TEST_GUILD_ID
import moneydash.settings.work as setts
from moneydash.settings.jobs import jobs
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
            await utils.add_exp(inter, (c_bottles - b_bottles) // 6)
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

    @tasks.loop(hours=24)
    async def loop_work(self):
        for user in db.get_all_accounts('''WHERE job != "None"'''):
            job = db.get_account(user)['job']
            db.update_account(user, ('bank', jobs[job]['salary']))
            await utils.add_exp(user, jobs[job]['exp'])


class Apply(nextcord.ui.View):
    def __init__(self, job):
        super().__init__()
        self.job = job

    @nextcord.ui.button(label='Устроиться на работу', style=nextcord.ButtonStyle.green)
    async def apply(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        data = db.get_account(inter.user.id)
        if data['level'] < jobs[self.job]['level']:
            await inter.response.send_message(embed=nextcord.Embed(title='Вы не подходите по уровню для этой профессии', colour=nextcord.Colour.red()), ephemeral=True)
            return
        await inter.response.edit_message(embed=nextcord.Embed(title='Новая работа!', description=f'Вы успешно устроились на работу {jobs[self.job]["name"]}!', colour=nextcord.Colour.green()))
        db.update_account(inter.user.id, ('job', self.job))
        if jobs[self.job]['badge'] != '' and jobs[self.job]['badge'] not in data['meta']['badges']:
            await inter.send('Получен новый значок! (Вы можете увидеть его в своём профиле - /profile)')
            data['meta']['badges'].append(jobs[self.job]['badge'])
            db.update_account(inter.user.id, ('meta', data['meta']))


class SelectJob(nextcord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Выберите вакансию",
            max_values=1,
            min_values=1,
            options=[nextcord.SelectOption(label=jobs[job]['name'], value=job, description=f'Требуемый уровень: {jobs[job]["level"]}') for job in jobs])

    async def callback(self, inter: Interaction):
        job = inter.data['values'][0]
        em = nextcord.Embed(
            title=f'Вакансии - {jobs[job]["name"]}', description=f'Требуемый уровень: {jobs[job]["level"]}', colour=nextcord.Colour.blurple())
        em.add_field(name='Зарплата/день', value=jobs[job]['salary'])
        em.add_field(name='Опыт/день', value=jobs[job]['exp'])
        view = Apply(job)
        view.add_item(SelectJob())
        await inter.response.edit_message(embed=em, view=view)


class Job(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command('jobs', 'Устроиться на работу/Просотреть список работ', [TEST_GUILD_ID])
    async def cmd_jobs(self, inter: Interaction):
        view = nextcord.ui.View(timeout=None)
        view.add_item(SelectJob())
        await inter.response.send_message(view=view)


def setup(bot):
    bot.add_cog(Work(bot))
    bot.add_cog(Job(bot))
