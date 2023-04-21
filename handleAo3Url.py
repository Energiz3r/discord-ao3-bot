from fetchao3story import parseStory
from utils import find_between, hasWorkBeenPosted, urlToWorkId
from pprint import pprint
import discord
from emoji import emojiLookup


async def handleAo3Url(message):
    url = 'https://archiveofourown.org/' + \
        find_between(message.content + ' ', 'archiveofourown.org/', ' ')
    workId = urlToWorkId(url)
    print('Fetching story id ' + workId + ' from AO3...')
    if hasWorkBeenPosted(workId):
        print('Work already posted, skipping.')
        return False
    else:
        story = parseStory(url, workId)

        if 'The Locked Tomb' not in story['fandom'] and 'Gideon the Ninth' not in story['fandom'] and 'Harrow the Ninth' not in story['fandom'] and 'Nona the Ninth' not in story['fandom'] and 'Alecto the Ninth' not in story['fandom']:
            print('Work belonged to another fandom, skipping.')
            return False

        def emoji(category, name):
            emojiName = emojiLookup[category][name]
            return str(discord.utils.get(message.guild.emojis, name=emojiName))
        emojiString = emoji('rating', story['rating']) + '' + emoji('category', story['category']) + '\n' + emoji(
            'warnings', story['warnings']) + '' + emoji('iswip', story['isWIP'])
        embed = discord.Embed(
            color=discord.Color.purple(),
            title=story['fullTitle'],
            description=story['fandom'],
            url=url,
            type='rich'
        )
        embed.set_author(
            name=story['author'],
            url=story['authorWorksUrl'],
            icon_url=story['authorIconUrl']
        )
        embed.set_thumbnail(
            url='https://archiveofourown.org/images/ao3_logos/logo_42.png')
        embed.add_field(
            name=story['summaryTruncated'],
            value=emojiString + '\n\n' + 'Shared by ' + message.author.mention,
            inline=False
        )
        embed.add_field(
            name='Words',
            value=story['wordCount'],
            inline=True
        )
        embed.add_field(
            name='Chapters',
            value=story['chapterCount'] + '/' + story['chapterCountTotal'],
            inline=True
        )
        embed.add_field(
            name='Kudos',
            value=story['kudos'],
            inline=True
        )

        if False:
            lastTagCat = ''
            for tag in story['tags']:
                if tag['tagCategory'] != lastTagCat:
                    embed.add_field(
                        name='\u200b',
                        value='\u200b',
                        inline=False
                    )
                    lastTagCat = tag['tagCategory']
                embed.add_field(
                    name=tag['tagCategory'],
                    value=tag['tagLabel'],
                    inline=True
                )
        embed.set_footer(
            text='Fic last updated: ' +
            story['lastUpdated'] +
            ' | Bot trouble? Hit up Tangles#6014 | WorkID: ' + story['workId']
        )
        print('Adding ' + workId + ' to already-posted list.')
        hasWorkBeenPosted(urlToWorkId(url), True)
        return embed
