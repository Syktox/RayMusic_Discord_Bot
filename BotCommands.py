import discord
from discord.ext import commands
import yt_dlp

bot = None
queues = {}

def play_next_in_queue(ctx, voice_client, guild_id):
    if guild_id in queues and queues[guild_id]:
        source = queues[guild_id].pop(0)
        voice_client.play(
            source,
            after=lambda e: play_next_in_queue(ctx, voice_client, guild_id)
        )
    else:
        queues.pop(guild_id, None)

@commands.command('join')
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

@commands.command(name='leave')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@commands.command(name='play')  #error here
async def play(ctx, link):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send("The bot is not connected to a voice channel!")
        return
    try:
        ydl_opts = {
            'format': 'bestaudio',
            'noplaylist': True,
            'extract_flat': False,
            'quiet': False,
            'force_generic_extractor': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            audio_url = info['url']
            
    except Exception as e:
        await ctx.send(f"Fehler beim Abrufen des Links: {str(e)}")
        return

    try:
        source = discord.FFmpegOpusAudio(audio_url, 
                                        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                                        options="-vn")
    except Exception as e:
        await ctx.send(f"Error creating audio source: {str(e)}")
        return
    
    guild_id = ctx.guild.id
    if guild_id in queues:
        queues[guild_id].append(source)
        await ctx.send(f"Added to queue! Current rank: {queues.qsize}")
    else:
        queues[guild_id] = [source]
        await ctx.send("Playing now!")
        play_next_in_queue(ctx, voice_client, guild_id)

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

@commands.command('skip')
async def skip(ctx):
    ctx.voice_client.stop()
    play_next_in_queue(ctx, ctx.guild.voice_client, ctx.guild.id)

@commands.command('clearPl')
async def clearPl(ctx):
    queues.clear()
    ctx.voice_client.stop()