import asyncio
import discord
import sqlite3
from discord.ext import commands
from modules.util import config, send, get
from ast import literal_eval


class NoInputValue(commands.CommandError):
    pass


class NoAnimeFound(commands.CommandError):
    pass


class Ani(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, NoInputValue):
            description = f"사용법: `{config()['prefix']}애니 [제목]`"
            return await send(self.bot, ctx, description)
        elif isinstance(error, NoAnimeFound):
            description = "입력하신 애니는 존재하지 않습니다."
            return await send(self.bot, ctx, description)
        else:
            description = f"알 수 없는 에러가 발생하였습니다. " \
                          f"자세한 에러 내용은 다음과 같습니다.```"\
                          f"\n{error}```"
            return await send(self.bot, ctx, description)

    async def wrap_embed(self, ctx, anime):
        status = anime[5]
        if anime[5] is None:
            status = '완결'
        censored = ''
        if anime[3] == '1':
            censored = '[성인] '

        embed = discord.Embed(title=censored + anime[1], description=status, color=0x3361B6)
        if anime[6]:
            embed.add_field(name="방영일", value=anime[6][:10], inline=False)
        embed.add_field(name="장르", value='```\n'+'\n'.join(literal_eval(anime[4]))+'```')
        embed.set_footer(text=self.bot.user.name,
                         icon_url=config()['profile'])
        embed.set_image(url=anime[2])
        return await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name='애니', aliases=['a'])
    async def anime(self, ctx, *, search=None):
        def replace_data(value):
            return value.lower().replace(' ', '').replace('♡', '').replace('-', '').replace('.', '') \
                .replace('!', '').replace('☆', '').replace('○', '').replace('~', '').replace('&', '') \
                .replace(':', '').replace('@', '').replace('#', '').replace('*', '').replace('(', '').replace(')', '') \
                .replace('+', '').replace('[', '').replace(']', '').replace('/', '').replace(',', '').replace('?', '') \
                .replace('`', '')

        def check(m):
            if m.author != ctx.author or m.channel != ctx.channel:
                return None
            try:
                c = int(m.content.strip(config()['prefix']))
            except ValueError:
                return None
            if len(queries) > c:
                return m.author == ctx.author and m.channel == ctx.channel

        if search is None:
            raise NoInputValue

        cursor = sqlite3.connect('laftel.db').cursor()
        queries = cursor.execute(f'SELECT * FROM anime WHERE name LIKE "%{search}%"').fetchall()
        if not queries:
            anime_data = cursor.execute('SELECT * FROM anime').fetchall()
            for anime in anime_data:
                if replace_data(search) in replace_data(anime[1]):
                    queries = cursor.execute(f'SELECT * FROM anime WHERE name = "{anime[1]}"').fetchall()

        if len(queries) == 0:
            raise NoAnimeFound
        elif len(queries) == 1:
            return await self.wrap_embed(ctx, queries[0])

        content = '```\n'
        count = 0
        for query in queries:
            content += f"{count}: {query[1]}\n"
            count += 1
        content += '```'
        embed = discord.Embed(
            title="애니를 선택하세요.",
            description=f"애니메이션의 좌측에 있는 숫자를 채팅창에 입력하세요."
                        f"\n{content}"
        )
        embed.set_footer(
            text=self.bot.user.name,
            icon_url=config()['profile']
        )
        message = await ctx.send(ctx.author.mention, embed=embed)
        try:
            respond = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            return await message.delete()
        await message.delete()
        await respond.delete()
        anime = queries[int(respond.content.strip(config()['prefix']))]
        return await self.wrap_embed(ctx, anime)


def setup(bot):
    bot.add_cog(Ani(bot))
