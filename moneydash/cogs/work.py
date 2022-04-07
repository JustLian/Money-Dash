from nextcord import Interaction, SlashOption
import nextcord
from nextcord.ext import commands
from moneydash import TEST_GUILD_ID


class Work(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @nextcord.slash_command('work', 'Начать подработку', [TEST_GUILD_ID])
    async def cmd_work(self, inter: Interaction, work: str = SlashOption('work', 'Тип работы: [bottles - сбор бутылок;]', True, choices=['bottles', 'test'])):
        await inter.response.send_message('TODO')
    

def setup(bot):
    bot.add_cog(Work(bot))