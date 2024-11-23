import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

def save_message(message):
    file = open('log.txt', 'a')
    file.write(f'{message.author} {message.content}\n')
    file.close()

intents = discord.Intents.default()
intents.message_content=True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('$play '):
        save_message(message)
        await message.channel.send('Hello!')

    if message.content.startswith('$pause'):
        pass

    if message.content.startswith('$resume'):
        pass

    if message.content.startswith('$skip'):
        pass

    if message.content.startswith('$stop'):
        pass

TOKEN = os.getenv('TOKEN')
bot.run(TOKEN)