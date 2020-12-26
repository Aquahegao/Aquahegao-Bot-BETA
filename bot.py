import os
from modules.util import config
from discord.ext import commands

bot = commands.Bot(command_prefix=config()['prefix'], case_insensitive=True)

for e in os.listdir('extensions'):
    if e == '__pycache__':
        continue
    try:
        bot.load_extension(f'extensions.{e.replace(".py", "")}')
    except Exception as error:
        print(f'{e} 로드 실패.\n{error}')

bot.run(config()['token'], bot=True, reconnect=True)
