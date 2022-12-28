from io import StringIO
from html.parser import HTMLParser
from pathlib import Path


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start


def hasWorkBeenPosted(workId, addToList=False):
    file = open(Path("workIDs.txt"), "r")
    lines = file.readlines()
    idDidExist = False
    for line in lines:
        if workId in line:
            idDidExist = True
    file.close()
    if (addToList):
        file2 = open(Path("workIDs.txt"), "a")
        if not idDidExist:
            file2.write(workId + '\n')
        file2.close()
    return idDidExist


def urlToWorkId(url):
    urlPath = url.split('archiveofourown.org/', 1)[1] + '/'
    result = urlPath[find_nth(urlPath, '/', 1)+1:find_nth(urlPath, '/', 2)]
    if '?' in result:
        return result.split('?')[0]
    else:
        return result
