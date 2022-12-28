import discord
from handleAo3Url import handleAo3Url

ficlist = "1036402049639796766"
ficUpdates = "1036787235447636039"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        if message.channel.name == 'ficlist' and 'Only fic links can be posted here' in message.content:
            await message.delete(delay = 5)
        return

    if 'archiveofourown.org/works/' in message.content:
        destChannel = await message.guild.fetch_channel(ficlist)
        storyEmbed = await handleAo3Url(message)
        if storyEmbed:
            await destChannel.send(embeds = (storyEmbed, ))
            if message.channel.name == 'ficlist':
                await message.delete()
            
    else:
        if message.channel.name == 'ficlist':
            await message.channel.send('Only fic links can be posted here! Deleting your message in 5 sec...')
            await message.delete(delay = 5)

    if  message.content.startswith('hayo') or message.content.startswith('Hayo') or message.content.startswith('HAYO'):
        await message.channel.send('Hayo!')

client.run('MTAzNjQzMzU0NzA0NjY4Njc1MQ.GqpI62.rGmKVIgTi-NHBKGg15j6IHGGkLOZgGDP7rIo_w')
