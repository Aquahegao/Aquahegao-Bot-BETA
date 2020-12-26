import discord
import json
import aiohttp
from bs4 import BeautifulSoup


def config():
    with open('config.json', 'r', encoding='utf-8-sig') as f:
        cfg = json.load(f)
        f.close()
    return cfg


async def send(bot, ctx, description):
    embed = discord.Embed(
        title="에러!",
        description=description,
        color=0xFF0000
    )
    embed.set_footer(
        text=bot.user.name,
        icon_url=config()['profile']
    )
    return await ctx.send(ctx.author.mention, embed=embed)


async def get(url, headers=None, parse_type='default'):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as r:
            if parse_type == 'default':
                text = await r.read()
                return BeautifulSoup(text, 'html.parser')
            else:
                text = await r.json()
                return text
