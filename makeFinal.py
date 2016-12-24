from customLemmatizer import customLemmatize
from makeFiles import getNameArray
from functools32 import lru_cache
import re
import os
import sys
from nltk.stem.wordnet import WordNetLemmatizer


def createFinalFile(fileName,companyName,lmtzr):
    try:
        documents = open(fileName)
    except (OSError, IOError) as e:
        return
    txt = ''
    for line in documents:
        txt += line
    documents.close()
    docPattern = re.compile('<DOCUMENT>(.*?)</DOCUMENT>')
    articles = re.findall(docPattern,txt)
    txt = ''
    articlePattern = re.compile('<ARTICLE>(.*?)</ARTICLE>')
    pricePattern   = re.compile('<PRICE>.*?</PRICE>')
    datePattern    = re.compile('<DATE>.*?</DATE>')
    eventPattern   = re.compile('<EVENTS>.*?</EVENTS>')
    for article in articles:
        body = re.findall(articlePattern,article)[0]
        body = ' '.join(customLemmatize(body,lmtzr))
        body = '<BODY>' + body + '</BODY>'
        price = re.findall(pricePattern,article)[0]
        date  = re.findall(datePattern,article)[0]
        events= re.findall(eventPattern,article)[0]
        txt += '<DOCUMENT>' + date + price + events + body + '</DOCUMENT>'
    try:
        fid = open('created/'+companyName+'_final.txt','w')
    except (OSError, IOError) as e:
        return
    fid.write(txt)
    fid.close()
    return

def Solution(fileName):
    lmtzr = WordNetLemmatizer()
    lmtzr = lru_cache(maxsize=50000)(lmtzr.lemmatize)
    companies = getNameArray(fileName)
    for company in companies:
        print 'Solving: '+company
        inputPath = 'created/' + company + '_new.txt'
        print 'Getting in.'
        createFinalFile(inputPath,company,lmtzr)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        Solution(sys.argv[1])
