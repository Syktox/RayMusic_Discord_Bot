import discord
from discord.ext import commands
import yt_dlp

bot = None

@commands.command('join')
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

@commands.command(name='leave')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@commands.command(name='play')
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
@commands.command(pass_content = True)
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

@commands.command('stop')
async def stop(ctx):
    if hasattr(bot, "ffmpeg_process"):
        bot.ffmpeg_process.terminate()
        await ctx.send("Recording stopp! Audio saved as `output.wav`.")
    else:
        await ctx.send("No active recording found.")

@commands.command('pause')
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        ctx.send("There is no audio playing")

@commands.command('resume')
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        ctx.send("No audio is paused")

@commands.command('playNext')
async def playNext(ctx, link):
    pass

@commands.command('clearPl')
async def clearPl(ctx):
    pass