import discord
from discord.ext import commands
from nozomi import api
from modules.util import config, send


class NoInputValue(commands.CommandError):
    pass


class IncludingBannedTag(commands.CommandError):
    pass


class NoGalleryFound(commands.CommandError):
    pass


class SSLError(commands.CommandError):
    pass


class Nozomi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, NoInputValue):
            description = f"사용법: `{config()['prefix']}히토미 [URL 또는 번호]`"
            return await send(self.bot, ctx, description)
        elif isinstance(error, IncludingBannedTag):
            description = "입력하신 작품에서 금지된 태그가 감지되었습니다."
            return await send(self.bot, ctx, description)
        elif isinstance(error, NoGalleryFound):
            description = "입력하신 작품은 존재하지 않습니다."
            return await send(self.bot, ctx, description)
        elif isinstance(error, SSLError):
            description = "HTTPS 우회 설정이 활성화되지 않았습니다."
            return await send(self.bot, ctx, description)
        else:
            description = f"알 수 없는 에러가 발생하였습니다. " \
                          f"자세한 에러 내용은 다음과 같습니다.```"\
                          f"\n{error}```"
            return await send(self.bot, ctx, description)

    @commands.command(name='노조미', aliases=['n', 'nozomi'])
    async def nozomi(self, ctx, *, search=None):
        if search is None:
            raise NoInputValue

        if 'nozomi.la' not in search:
            try:
                int(search)
            except ValueError:
                raise NoGalleryFound
            art_id = search.split(' ')[0]
        else:
            art_id = search.split('/')[-1].strip('.html')
            try:
                int(art_id)
            except ValueError:
                art_id = art_id.split('-')[-1]

        await ctx.trigger_typing()
        url = f'https://nozomi.la/post/{art_id}.html'
        post = api.get_post(url)

        tags = ''
        for i in post.general[:15]:
            tags += f'{i.tagname_display}\n'

        if len(post.general) > 15:
            tags += '...'

        embed = discord.Embed(
            description=f'[보러가기](https://nozomi.la/post/{art_id}.html)',
            color=0xe29fc9)
        embed.add_field(name='태그', value=tags, inline=False)
        embed.add_field(name='업로드 날짜', value=post.date.split(' ')[0], inline=False)
        embed.set_image(url=post.imageurl)
        embed.set_footer(
            text=self.bot.user.name,
            icon_url=config()['profile'])
        return await ctx.send(ctx.author.mention, embed=embed)


def setup(bot):
    bot.add_cog(Nozomi(bot))
