import nextcord


def add_author(embed: nextcord.Embed, user: nextcord.User):
    if user.avatar is None:
        embed.set_author(name=user.name)
    else:
        embed.set_author(name=user.name, icon_url=user.avatar.url)
