import discord

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print(f'We have logged in as {client}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
