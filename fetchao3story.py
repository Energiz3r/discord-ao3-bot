import requests
from utils import find_between, strip_tags, urlToWorkId

session = requests.session()

def parseStory(url, workId):
    story = {}
    # get workId from the URL
    story['workId'] = workId

    # fetch the page and get author info from it
    page = session.get(url)
    story['author'] = find_between(page.text, '<a rel="author" href="', '</a>').split(">",1)[1]
    story['chapterTitle'] = ''
    if 'chapters/' in url and '<div class="chapter preface group" role="complementary">' in page.text:
        chapterBlock = find_between(page.text, '<div class="chapter preface group" role="complementary">', '</h3>') + '</h3>'
        chapterLine = find_between(chapterBlock, '<h3 class="title">', '</h3>')
        chapterLabel = find_between(chapterLine, '">', '</a>')
        story['chapterTitle'] = chapterLabel + find_between(chapterLine, '</a>', '\n')
    authorUrlName = story['author'] if not '(' in story['author'] else find_between(story['author'], '(', ')')
    story['authorWorksUrl'] = 'https://archiveofourown.org/users/' + authorUrlName + '/works'

    # fetch author's page to grab icon URL
    authorUrl = find_between(page.text, '<a rel="author" href="', '">')
    authorUrlSubstr = find_between(page.text, '<a rel="author" href="/users/', '">')
    page = session.get('https://archiveofourown.org' + authorUrl)
    authorIconBlock = find_between(page.text, '<p class="icon"><a href="/users/' + authorUrlSubstr + '"><img', '</a></p>')
    story['authorIconUrl'] = find_between(authorIconBlock, 'src="', '"/>')
    if 'images/skins/iconsets/default/' in story['authorIconUrl']:
        story['authorIconUrl'] = 'https://archiveofourown.org/' + story['authorIconUrl']

    # fetch the author's works listing page and get the block of content for the work from it
    page = session.get(story['authorWorksUrl'])
    workBlock = ""
    pagesBlock = find_between(page.text, '<h4 class="landmark heading">Pages Navigation</h4>', '</a></li></ol>')
    numPages = 1
    if len(pagesBlock) > 0:
        print('Author has multiple pages of works...')
        pageBlocksAr = pagesBlock.split('<a')
        lastPageBlock = pageBlocksAr[len(pageBlocksAr) - 2]
        pageNumText = find_between(lastPageBlock, '">', '</a>')
        numPages = int(pageNumText)
        print(str(numPages) + ' pages of works found.')

    curPage = 1
    while not len(workBlock) > 0 and curPage <= numPages:
        workBlock = find_between(page.text, '<li id="work_' + story['workId'], '</li>\n<li id="work')
        if not len(workBlock) > 0:
            workBlock = find_between(page.text, '<li id="work_' + story['workId'], '</ol>')
        if len(workBlock) > 0:
            break
        print('Did not find workBlock on pages ' + str(curPage) + ' of works...')
        curPage = curPage + 1
        page = session.get(story['authorWorksUrl'] + '?page=' + str(curPage))

    if not len(workBlock) > 0:
        print('Could not find work html block', story['authorWorksUrl'])

    # parse contents off the work listing block
    story['fandom'] = find_between(workBlock, '<span class="landmark">Fandoms:</span>', '</a>').split(">",1)[1]
    story['fandomUrl'] = find_between(workBlock, '<span class="landmark">Fandoms:</span>', '">').split('href="',1)[1]
    story['workTitle'] = find_between(workBlock, '<h4 class="heading">', '</a>').split(">",1)[1]
    story['fullTitle'] = story['workTitle'] + ', ' + story['chapterTitle'] if len(story['chapterTitle']) > 0 else story['workTitle']
    story['rating'] = find_between(workBlock, '<span class="rating-', ' rating')
    story['warnings'] = find_between(workBlock, '<span class="warning-', ' warnings')
    story['category'] = find_between(workBlock, '<span class="category-', ' category')
    story['isWIP'] = find_between(workBlock, '<span class="complete-', ' iswip')
    story['wordCount'] = find_between(workBlock, '<dd class="words">', '</dd>')
    story['chapterCountUrl'] = ''
    if '<dd class="chapters"><a href="' in workBlock:
        story['chapterCount'] = find_between(workBlock, '<dd class="chapters"><a href="', '</a>').split(">",1)[1]
        story['chapterCountTotal'] = find_between(workBlock, '<dd class="chapters"><a href="', '</dd').split("</a>/",1)[1]
        story['chapterCountUrl'] = find_between(workBlock, '<dd class="chapters"><a href="', '">')
    else:
        chapters = find_between(workBlock, '<dd class="chapters">', '</dd>')
        story['chapterCount'] = chapters.split('/')[0]
        story['chapterCountTotal'] = chapters.split('/')[1]
    story['kudos'] = '0'
    story['kudosUrl'] = ''
    if '<dd class="kudos"><a href="' in workBlock:
        story['kudos'] = find_between(workBlock, '<dd class="kudos"><a href="', '</a></dd>').split('">',1)[1]
        story['kudosUrl'] = find_between(workBlock, '<dd class="kudos"><a href="', '">')
    story['bookmarksCount'] = '0'
    story['bookmarksUrl'] = ''
    if '<dd class="bookmarks"><a href="' in workBlock:
        story['bookmarksCount'] = find_between(workBlock, '<dd class="bookmarks"><a href="', '</a></dd>').split('">',1)[1]
        story['bookmarksUrl'] = find_between(workBlock, '<dd class="bookmarks"><a href="', '">')
    story['commentsCount'] = '0'
    story['commentsUrl'] = '0'
    if '<dd class="comments"><a href="' in workBlock:
        story['commentsCount'] = find_between(workBlock, '<dd class="comments"><a href="', '</a></dd>').split('">',1)[1]
        story['commentsUrl'] = find_between(workBlock, '<dd class="comments"><a href="', '">')
    story['lastUpdated'] = find_between(workBlock, '<p class="datetime">', '</p>')
    story['language'] = find_between(workBlock, '<dd class="language">', '</dd>')
    story['hits'] = find_between(workBlock, '<dd class="hits">', '</dd>')
    summaryBlock = find_between(workBlock, '<blockquote class="userstuff summary">', '</blockquote>')
    summary = strip_tags(summaryBlock).strip()
    story['summaryFull'] = summary
    story['summaryTruncated'] = (summary[:200] + '...') if len(summary) > 200 else summary
    tagsBlock = find_between(workBlock, '<ul class="tags commas">', '</ul>')
    tagElements = tagsBlock.strip().split('</li>')
    story['tags'] = []
    for tagStr in tagElements:
        tagStrCleaned = tagStr.strip()
        if len(tagStrCleaned) > 0:
            tag = tagStrCleaned + '</li>'
            thisTag = {}
            thisTag['tagCategory'] = find_between(tag, "<li class='", "'>")
            tagContents = find_between(tag, "'>", "</li>")
            if '<strong>' in tagContents:
                tagContents = find_between(tag, "<strong>", "</strong>")
            thisTag['tagUrl'] = find_between(tagContents, '<a class="tag" href="', '">')
            thisTag['tagLabel'] = find_between(tagContents, '">', '</a>')
            story['tags'].append(thisTag)
    if len(story['workTitle']) > 0:
        print('Story successfully fetched')
    return story

#print(parseStory('https://archiveofourown.org/works/42806565'))