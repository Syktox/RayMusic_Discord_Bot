import discord
from discord.ext import commands
import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import asyncio
import os

# Configure Spotify API
SPOTIFY_CLIENT_ID = "4506e5a4f4444c6db229325b3b1a2425"
SPOTIFY_CLIENT_SECRET = "136b75613302468bac61e37f246b29c5"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
))

voice_clients = {}

@commands.command(name="join")
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_clients[ctx.guild.id] = await channel.connect()
    else:
        await ctx.send("You need to be in a voice channel to use this command.")

@commands.command(name="leave")
async def leave(ctx):
    if ctx.guild.id in voice_clients:
        await voice_clients[ctx.guild.id].disconnect()
        del voice_clients[ctx.guild.id]
    else:
        await ctx.send("I'm not in a voice channel.")

@commands.command(name="play")
async def play(ctx, *, query):
    if ctx.guild.id not in voice_clients:
        await join(ctx)

    voice_client = voice_clients[ctx.guild.id]
    
    if "open.spotify.com" in query:
        if "track" in query:
            results = sp.track(query)
            query = results['name'] + " " + results['artists'][0]['name']
        else:
            await ctx.send("Only Spotify track links are supported.")
            return

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song.mp3',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)
        url = info['entries'][0]['webpage_url']

    voice_client.stop()
    voice_client.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: os.remove("song.mp3"))
    await ctx.send(f"Now playing: {query}")

@commands.command(name="pause")
async def pause(ctx):
    if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_playing():
        voice_clients[ctx.guild.id].pause()
    else:
        await ctx.send("No music is currently playing.")

@commands.command(name="resume")
async def resume(ctx):
    if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_paused():
        voice_clients[ctx.guild.id].resume()
    else:
        await ctx.send("No music is currently paused.")

# Stop the music
@commands.command(name="stop")
async def stop(ctx):
    if ctx.guild.id in voice_clients:
        voice_clients[ctx.guild.id].stop()
    else:
        await ctx.send("No music is currently playing.")

