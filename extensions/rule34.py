import discord
from discord.ext import commands
import aiohttp
from modules.util import config, send, get


class NoInputValue(commands.CommandError):
    pass


class NotValidURL(commands.CommandError):
    pass


class SSLError(commands.CommandError):
    pass


class Rule34(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, NoInputValue):
            description = f"사용법: `{config()['prefix']}룰34 [URL]`"
            return await send(self.bot, ctx, description)
        elif isinstance(error, NotValidURL):
            description = "링크를 입력해주세요."
            return await send(self.bot, ctx, description)
        elif isinstance(error, SSLError):
            description = "HTTPS 우회 설정이 활성화되지 않았습니다."
            return await send(self.bot, ctx, description)
        else:
            description = f"알 수 없는 에러가 발생하였습니다. " \
                          f"자세한 에러 내용은 다음과 같습니다.```"\
                          f"\n{error}```"
            return await send(self.bot, ctx, description)

    async def wrap_embed(self, ctx, title, link, tags, thumbnail):
        embed = discord.Embed(title=title, color=0xACE4A3,
                              description=f'\n[보러가기]({link})')
        embed.add_field(name='태그', value=tags, inline=False)
        embed.set_image(url=thumbnail)
        embed.set_footer(
            text=self.bot.user.name,
            icon_url=config()['profile']
        )
        return await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name='룰34', aliases=['rule', '룰', 'r'])
    async def rule34(self, ctx, *, search=None):
        await ctx.trigger_typing()
        if search is None:
            raise NoInputValue

        elif 'rule34.paheal.net' in search:
            try:
                soup = await get(search, config()['header'])
            except aiohttp.ClientConnectorError:
                raise SSLError
            thumbnail = soup.select_one('#main_image')['src']
            tags = soup.select_one('#tag_editor')['value'].replace(' ', '\n').replace('_', ' ')
            return await self.wrap_embed(ctx, 'Rule34(Paheal)', search, tags, thumbnail)

        elif 'rule34.xxx' in search:
            art_id = search.split("=")[-1]
            url = f'https://r34-json-api.herokuapp.com/posts?id={art_id}'
            js = await get(url, parse_type='js')
            thumbnail = js[0]['file_url']
            tag = js[0]['tags']
            tags = ''
            if len(tag) >= 10:
                for t in tag[:11]:
                    tags += f'{t.replace("_", "").title()}\n'
                tags += f'···'
            else:
                for t in tag:
                    tags += f'{t.replace("_", "").title()}\n'
            url = f'https://rule34.xxx/index.php?page=post&s=view&id={art_id}'
            return await self.wrap_embed(ctx, 'Rule34', url, tags, thumbnail)

        else:
            raise NotValidURL


def setup(bot):
    bot.add_cog(Rule34(bot))
