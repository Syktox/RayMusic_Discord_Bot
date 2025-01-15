import discord
from discord.ext import commands
import datetime

bot = None

def save_message(message):
    file = open('log.txt', 'a')
    file.write(f'{message.author} {message.content}\n')
    file.close()
        
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Command not found!")
    elif isinstance(error, discord.ext.commands.errors.BadBoolArgument):
        await ctx.send(f"Wrong Input! You should use True or False")
    elif isinstance(error, discord.errors.ClientException):
        await ctx.send("ClientException")
    else:
        raise error

async def on_ready():
    print(f"Logged in as {bot.user.name} "
            f"at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")

async def on_message(message):
    if message.author == bot.user:
        return
    save_message(message)
    await bot.process_commands(message)
