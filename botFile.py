import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import yt_dlp
import asyncio

def save_message(message):
    file = open('log.txt', 'a')
    file.write(f'{message.author} {message.content}\n')
    file.close()

def run_bot():
    TOKEN = os.getenv('TOKEN')
    intents = discord.Intents.default()
    intents.voice_states=True
    intents.message_content=True
    bot = commands.Bot(command_prefix='$', intents=intents)

    playlist = {}


    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        save_message(message)
        await bot.process_commands(message)


    @bot.command(name='join')
    async def join(ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                try:
                    await channel.connect()
                    await ctx.send(f'Joined {channel.name}!')
                    return True
                except discord.ClientException as e:
                    await ctx.send(f"Error: {e}")
                    return False
            else:
                await ctx.send("I'm already connected to a voice channel!")
                return False
        else:
            await ctx.send("You need to be in a voice channel for me to join!")
            return False

    @bot.command(name='leave')
    async def leave(ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("I'm not connected to a voice channel!")

    @bot.command(name='play')
    async def play(ctx, link):
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice_clinet = bot.voice_clients
        if not voice_client:
            await ctx.send("The bot is not connected to a voice channel!")
            return
        
        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'noplaylist': True}) as ydl:
            info = ydl.extract_info(link, download=False)
            audio_url = info['url']
            
        voice_client.stop()
        source = await discord.FFmpegOpusAudio.from_probe(audio_url)
        voice_client.play(source)

    @bot.command()
    async def listen(ctx):
        joined = await join(ctx)
        if (joined):
            print("Listening")

    bot.run(TOKEN)