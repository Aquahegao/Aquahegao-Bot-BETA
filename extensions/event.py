import discord
from discord.ext import commands


class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('='*40)
        print(f'{self.bot.user.name}(으)로 로그인합니다.')
        print(f'접속 중인 서버: {len(self.bot.guilds)}개')
        print('=' * 40)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return None


def setup(bot):
    bot.add_cog(Event(bot))