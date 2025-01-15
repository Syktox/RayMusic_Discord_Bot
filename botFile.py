import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

import EventHandler
import BotCommands

load_dotenv()
playlist = []

def run_bot():
    token = os.getenv('TOKEN')
    intents = discord.Intents.default()
    intents.voice_states=True
    intents.message_content=True
    bot = commands.Bot(command_prefix='$', intents=intents)

    EventHandler.bot = bot
    BotCommands.bot = bot

    for event_name in dir(EventHandler):
        if event_name.startswith('on_'):
            event_func = getattr(EventHandler, event_name)
            bot.event(event_func)
    
    for command_name in dir(BotCommands):
        command_func = getattr(BotCommands, command_name)
        if isinstance(command_name, commands.Command):
            bot.command(command_func)

    bot.run(token)