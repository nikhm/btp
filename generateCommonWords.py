import re
import sys
from makeFiles import getNameArray

def getArticles(path):
    txt = ''
    try:
        fileID = open(path)
    except (OSError, IOError) as e:
        return txt
    for line in fileID:
        txt += line
    fileID.close()
    articlePattern = re.compile('<BODY>(.*?)</BODY>')
    articles = re.findall(articlePattern,txt)
    txt = ''
    for article in articles:
        txt += (article + ' ')
    return txt


def Solution(fileName):
    companies = getNameArray(fileName)
    wordList = {}
    for company in companies:
        print 'Collected from: ' + company
        pathName = 'created/' + company + '_final.txt'
        txt = getArticles(pathName)
        if txt == '':
            continue
        txt = txt.split(' ')
        lenTxt = len(txt)
        for i in range(lenTxt):
            if txt[i] in wordList:
                wordList[txt[i]] += 1
            else:
                wordList[txt[i]] = 1
    words = [(i,j) for (j,i) in wordList.items()]
    words = sorted(words)
    lenW = len(words)
    ret = []
    for i in range(lenW-1,0,-1):
        ret.append(words[i])
    return ret


if __name__=='__main__':
    if len(sys.argv) > 1:
        words = Solution(sys.argv[1]) # Specify sp500.txt as command line argument
        print words[1:200]
        N = 2000
        fileID = open('commonWords.txt','w')
        for i in range(N):
            if i < len(words):
                fileID.write(words[i][1]+' ')
