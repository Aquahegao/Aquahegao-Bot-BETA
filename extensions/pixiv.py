import discord
from discord.ext import commands
from modules.util import config, send
from modules.SauceNAO import *


class SimilarityTooLow(commands.CommandError):
    pass


class NoInputValue(commands.CommandError):
    pass


class NotValidURL(commands.CommandError):
    pass


class Pixiv(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, SimilarityTooLow):
            description = "전송하신 이미지와 비슷한 일러스트를 찾을 수 없습니다."
            return await send(self.bot, ctx, description)
        elif isinstance(error, NoInputValue):
            description = f"사용법: `{config()['prefix']}픽시브 [URL 또는 사진]`"
            return await send(self.bot, ctx, description)
        elif isinstance(error, NotValidURL):
            description = "링크를 입력해주세요."
            return await send(self.bot, ctx, description)
        else:
            description = f"알 수 없는 에러가 발생하였습니다. " \
                          f"자세한 에러 내용은 다음과 같습니다.```" \
                          f"\n{error}```"
            return await send(self.bot, ctx, description)

    @commands.command(name='픽시브', aliases=['p', 'pixiv'])
    async def pixiv(self, ctx, *, search=None):
        async def get_data(link):
            await ctx.trigger_typing()
            sauce = sn.get_sauce(link)
            sim = sauce['results'][0]['header']['similarity']
            thumb = sauce['results'][0]['header']['thumbnail']
            url = sauce['results'][0]['data']['ext_urls'][0]
            try:
                title = sauce['results'][0]['data']['title']
            except KeyError:
                raise SimilarityTooLow
            author = sauce['results'][0]['data']['member_name']

            if float(sim) < 80:
                raise SimilarityTooLow

            embed = discord.Embed(
                title=title,
                color=0x228d7f,
                description=f'**저자**: {author}\n\n'
                            f'유사도: {sim}\n'
                            f'[보러가기]({url})')
            embed.set_thumbnail(url=thumb)
            embed.set_footer(
                icon_url=config()['profile'],
                text=self.bot.user.name)
            await ctx.send(embed=embed)

        sn = SauceNAO(config()['sauce_token'], dbmask=8191, numres=12)

        if search:
            if 'http' not in search:
                raise NotValidURL
            return await get_data(search)
        elif not search and len(ctx.message.attachments) > 0:
            for i in range(0, len(ctx.message.attachments)):
                await get_data(ctx.message.attachments[i].url)
        else:
            raise NoInputValue


def setup(bot):
    bot.add_cog(Pixiv(bot))
