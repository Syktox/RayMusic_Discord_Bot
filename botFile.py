import os
import datetime
import subprocess
from zipfile import error

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
import yt_dlp

def save_message(message):
    file = open('log.txt', 'a')
    file.write(f'{message.author} {message.content}\n')
    file.close()

show_new_member_message = True

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
        if show_new_member_message:
            channel = member.guild.system_channel
            if channel:
                await channel.send(f"Hello {member.name}!")

    @bot.command('change_member_message')
    async def change_member_message(ctx, changed: bool):
        try:
            global show_new_member_message
            show_new_member_message = changed
            await ctx.send(f"Show new member message has been set to: {show_new_member_message}")
        except:
            await ctx.send("Error changing setting")

    @bot.command('check_member_message_status')
    async def check_member_message_status(ctx):
        await ctx.send(f"Show new member messages are set to: {show_new_member_message}")


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
        await join(ctx)

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
    @bot.command()
    async def record(ctx):
        if ctx.voice_client and ctx.voice_client.is_connected():
            ffmpeg_process = start_ffmpeg(ctx.voice_client)
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

    def start_ffmpeg(voice_client):
        """Start ffmpeg process to capture raw audio from Discord"""
        try:
            # Define ffmpeg command to capture and save raw PCM to a WAV file
            ffmpeg_command = [
                "ffmpeg",
                "-y",  # Overwrite output file if it exists
                "-f", "s16le",  # Specify raw PCM input
                "-ar", "48000",  # Audio sampling rate
                "-ac", "2",  # Number of audio channels
                "-i", "pipe:0",  # Read input from stdin (voice stream)
                "output.wav"  # Save output as a WAV file
            ]

            # Start ffmpeg as a subprocess and pipe audio from Discord
            ffmpeg_process = subprocess.Popen(
                ffmpeg_command,
                stdin=subprocess.PIPE
            )

            # Attach ffmpeg to the bot's audio stream
            voice_client.listen(discord.PCMAudio(ffmpeg_process.stdin))
            return ffmpeg_process
        except Exception as e:
            print(f"Failed to start ffmpeg: {e}")
            return None


    bot.run(token)