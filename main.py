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
intents.voice_states=True
intents.message_content=True
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    save_message(message)

    if message.content.startswith('$play'):
        await message.channel.send('$join')
        await message.channel.send('Hello')

    if message.content.startswith('$pause'):
        pass

    if message.content.startswith('$resume'):
        pass

    if message.content.startswith('$skip'):
        pass

    if message.content.startswith('$stop'):
        pass
    await bot.process_commands(message)


@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            try:
                await channel.connect()
                await ctx.send(f'Joined {channel.name}!')
            except discord.ClientException as e:
                await ctx.send(f"Error: {e}")
        else:
            await ctx.send("I'm already connected to a voice channel!")
    else:
        await ctx.send("You need to be in a voice channel for me to join!")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not connected to a voice channel!")


TOKEN = os.getenv('TOKEN')
bot.run(TOKEN)