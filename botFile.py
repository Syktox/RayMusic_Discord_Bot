import os
import datetime
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv
import yt_dlp
import json

load_dotenv()

show_join_message = True
show_leave_message = True

def save_message(message):
    file = open('log.txt', 'a')
    file.write(f'{message.author} {message.content}\n')
    file.close()

def run_bot():
    token = os.getenv('TOKEN')
    intents = discord.Intents.default()
    intents.voice_states=True
    intents.message_content=True
    bot = commands.Bot(command_prefix='$', intents=intents)

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Command not found!")
        elif isinstance(error, discord.ext.commands.errors.BadBoolArgument):
            await ctx.send(f"Wrong Input! You should use True or False")
        else:
            raise error

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user.name} "
              f"at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        save_message(message)
        await bot.process_commands(message)

    @bot.event
    async def on_member_join(ctx, member):
        if show_join_message:
            channel = member.guild.system_channel
            if channel:
                await channel.send(f"Hello {member.name}!")

    @bot.event
    async def on_member_remove(ctx, member):
        if show_leave_message:
            channel = member.guild.system_channel
            if channel:
                await channel.send(f"Goodbye {member.name}")

    @bot.command('change_join_message')
    async def change_join_message(ctx, changed: bool):
        global show_join_message
        show_join_message = changed
        await ctx.send(f"Show new member message has been set to: {show_join_message}")

    @bot.command('change_leave_message')
    async def change_leave_message(ctx, changed: bool):
        global show_leave_message
        show_leave_message = changed
        await ctx.send(f"Leave message has been set to: {show_leave_message}")

    @bot.command('check_join_message_status')
    async def check_join_message_status(ctx):
        await ctx.send(f"Join messages are set to: {show_join_message}")

    @bot.command('check_leave_message_status')
    async def check_leave_message_status(ctx):
        await ctx.send(f"Leave message are set to: {show_leave_message}")

    @bot.command('joke')
    async def joke(ctx):
        joke_url = "https://jokes-always.p.rapidapi.com/family"
        headers = {
            "x-rapidapi-key": "26a2dd88d8msha7adc935319e071p1d680fjsna2c3a5194d08",
            "x-rapidapi-host": "jokes-always.p.rapidapi.com"
        }
        response = requests.get(joke_url, headers=headers)
        await ctx.send(json.loads(response.text)['data'])

    @bot.command('join')
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

    @bot.command(name='play')
    async def play(ctx, link):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            ctx.send(f"You aren't in a voice channel")

        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if not voice_client:
            await ctx.send("The bot is not connected to a voice channel!")
            return
        
        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'noplaylist': True}) as ydl:
            info = ydl.extract_info(link, download=False)
            audio_url = info['url']
            
        voice_client.stop()
        source = await discord.FFmpegOpusAudio.from_probe(audio_url)
        voice_client.play(source)

    # other functionality should be used to record voice
    @bot.command(pass_content = True)
    async def record(ctx):
        if ctx.voice_client and ctx.voice_client.is_connected():
            ffmpeg_process = False  # need to be changed
            if ffmpeg_process:
                await ctx.send("Recording started! Use `!stop` to stop recording.")
                bot.ffmpeg_process = ffmpeg_process
            else:
                await ctx.send("Failed to start recording.")
        else:
            await ctx.send("I am not connected to a voice channel!")

    @bot.command('stop')
    async def stop(ctx):
        if hasattr(bot, "ffmpeg_process"):
            bot.ffmpeg_process.terminate()
            await ctx.send("Recording stopp! Audio saved as `output.wav`.")
        else:
            await ctx.send("No active recording found.")

    @bot.command('pause')
    async def pause(ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.pause()
        else:
            ctx.send("There is no audio playing")

    @bot.command('resume')
    async def resume(ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            voice.resume()
        else:
            ctx.send("No audio is paused")

    @bot.command('playNext')
    async def playNext(ctx, link):
        pass

    @bot.command('clearPl')
    async def clearPl(ctx):
        pass


    bot.run(token)