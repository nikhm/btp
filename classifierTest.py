import cPickle
from sklearn.ensemble import RandomForestClassifier
from makeFiles import getNameArray
import re
import sys
import datetime

def initDict():
    wordList = {}
    fID = open('commonWords.txt')
    txt = ''
    for line in fID:
        txt += line
    txt = txt.split(' ')
    for word in txt:
        wordList[word] = 0
    return wordList

def getVectors(fileName):
    try:
        fID = open(fileName)
    except (OSError, IOError) as e:
        return ([],[])
    txt = ''
    for line in fID:
        txt += line
    X,y = [],[]
    docPattern     = re.compile('<DOCUMENT>(.*?)</DOCUMENT>')
    bodyPattern    = re.compile('<BODY>(.*?)</BODY>')
    pricePattern   = re.compile('<PRICE>(.*?)</PRICE>')
    datePattern    = re.compile('<DATE>(.*?)</DATE>')
    eventPattern   = re.compile('<EVENTS>(.*?)</EVENTS') # A mistake creeped in while build final.txt so no >
    articles = re.findall(docPattern,txt)
    for article in articles:
        dateString = re.findall(datePattern,article)[0]
        dateString = dateString.split('/')
        dateString = [int(z) for z in dateString]
        today = datetime.datetime(dateString[0],dateString[1],dateString[2])
        if today <= datetime.datetime(2010,1,1):
            continue
        doc = re.findall(bodyPattern,article)[0]
        dummy = doc.split(' ')
        wordList = initDict()
        if len(dummy) < 20:
            continue
        for word in dummy:
            if word in wordList:
                wordList[word] += 1
        price = re.findall(pricePattern,article)[0]
        price = price.split(',')
        price = [float(z) for z in price]
        [prevPrice,postPrice,prevSP,postSP,wPrice,mPrice,yPrice] = price
        yt = ((postPrice - prevPrice)*100.0)/prevPrice
        yt -= ((postSP - prevSP)*100.0)/prevSP
        if yt*yt > 0.25:
            if yt > 0:
                yt = 1
            else:
                yt = -1
        else:
            yt = 0
        wpp = ((prevPrice-wPrice)*100.0)/wPrice
        mpp = ((prevPrice-mPrice)*100.0)/mPrice
        ypp = ((prevPrice-yPrice)*100.0)/yPrice
        events = list(re.findall(eventPattern,article)[0])
        events = [1 if x=='1' else 0 for x in events]
        Xt = []
        for word in wordList.items():
            Xt.append(word[1])
        for i in events:
            Xt.append(i)
        Xt.append(wpp)
        Xt.append(mpp)
        Xt.append(ypp)
        X.append(Xt)
        y.append(yt)
    return (X,y)



def Solution(fileName):
    companies = getNameArray(fileName)
    X,y = [],[]
    for company in companies:
        print 'Generating from: ' + company
        inputFile = 'created/' + company + '_final.txt'
        (tmpX,tmpY) = getVectors(inputFile)
        lenX = len(tmpX)
        if lenX < 1:
            continue
        for i in range(lenX):
            X.append(tmpX[i])
            y.append(tmpY[i])
    return (X,y)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        (X,y) = Solution(sys.argv[1])
        fid = open('rfClassifier.pkl')
        forest = cPickle.load(fid)
        yPred = forest.predict(X)
        lenVec = len(y)
        cnt = 0
        print y[1:100]
        print yPred[1:100]
        numOther,numLabel = 0,0
        for i in range(lenVec):
            numLabel += (y[i]*y[i])
            numOther += (yPred[i]*yPred[i])
            if abs(y[i] - yPred[i]) <= 0.1:
                cnt += 1
        print 'Percentage correct: ' + str((float(cnt)/float(lenVec)) *100.0)
        print numOther
        print numLabel
