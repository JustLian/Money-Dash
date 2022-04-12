import nextcord
from moneydash import db


def add_author(embed: nextcord.Embed, user: nextcord.User):
    if user.avatar is None:
        embed.set_author(name=user.name)
    else:
        embed.set_author(name=user.name, icon_url=user.avatar.url)


async def add_exp(inter, amount: int) -> None:
    if isinstance(inter, nextcord.Interaction):
        db.update_account(inter.user.id, ('exp', amount))
        data = db.get_account(inter.user.id)
        if data['exp'] >= data['level'] * 12:
            db.update_account(inter.user.id, ('exp', -12 *
                                              data['level']), ('level', 1))
            await inter.send(embed=nextcord.Embed(title='Новый уровень!', description=f'Вы получили {data["level"] + 1} уровень.', colour=nextcord.Colour.gold()))
    else:
        db.update_account(inter, ('exp', amount))
        data = db.get_account(inter)
        if data['exp'] >= data['level'] * 12:
            db.update_account(
                inter, ('exp', -12 * data['level']), ('level', 1))
