import nltk
import re
import datetime
import sys
import csv

def searchForPrev(l,dt,lo=0,hi=None):
    if hi == None:
        hi = len(l) - 1
    if lo > hi:
        return []
    if (lo == hi) or (lo+1 == hi):
        if (lo == hi):
            #print lo
            return [l[lo][0],l[lo][2],l[lo+1][1]]
        else:
            if l[hi][0] < dt:
                return [l[hi][0],l[hi][2],l[hi][1]]
            else:
                return [l[lo][0],l[lo][2],l[lo+1][1]]
    mid = (lo+hi)/2
    if dt < l[mid][0]:
        return searchForPrev(l,dt,lo,mid)
    else:
        #print dt,l[mid][0]
        return searchForPrev(l,dt,mid+1,hi)


def getDateTime(s):
    q,l = s.split('/'),[]
    for i in q:
        l.append(int(float(i)))
    dt = datetime.datetime(l[0],l[1],l[2])
    return dt

def convert2standard(s):
    year,month,day = s[0:4],s[4:6],s[6:8]
    ret = year + '/' + month + '/' + day
    return ret

def getWMY(dtf,stockRows):
    wPrice = searchForPrev(stockRows,dtf-datetime.timedelta(days=-7))
    wPrice = wPrice[2] if len(wPrice)>0 else -1
    mPrice = searchForPrev(stockRows,dtf-datetime.timedelta(weeks=-4))
    mPrice = mPrice[2] if len(mPrice)>0 else -1
    yPrice = searchForPrev(stockRows,dtf-datetime.timedelta(days=-365))
    yPrice = yPrice[2] if len(yPrice)>0 else -1
    return [wPrice,mPrice,yPrice]

def getEventVector(doc,eventList):
    s = ''
    for event in eventList:
        if event in doc:
            s += '1'
        else:
            s += '0'
    return s

def solve(name):
    folderIn = 'data/'
    folderOut = 'created/'
    try:
        #file = open(name).read()
        file = open(folderIn + name)
    except (OSError, IOError) as e:
        return

    txt = ""

    for line in file:
        txt += line

    txt = txt.replace('\n',' ')
    txt = txt.replace('\r',' ')

    #print txt
    pattern = re.compile('<DOCUMENT>(.*?)</DOCUMENT>')

    docs = re.findall(pattern,txt)
    docLen = len(docs)

    #print docLen
    #print docs[0:5]

    # We have all the documents in docs
    newFileName = folderOut + name + '_new.txt'

    try:
        out = open(newFileName,'w')
    except (OSError, IOError) as e:
        return

    txt = ""

    # Create a separate file for each of the companies
    # date
    # Article
    # STOCK : BEFORE AFTER (COMPANY)  BEFORE AFTER (S&P 500)

    reader = csv.DictReader(open(folderIn + name + '.csv'))

    stockRows = []

    for row in reader:
        dateString = '/'.join(row['Date'].split('-'))
        dt = getDateTime(dateString)
        listNum = []
        listNum.append(dt)
        listNum.append(float(row['Open']))
        listNum.append(float(row['Close']))
        stockRows.append(listNum)

    spRows = []
    reader = csv.DictReader(open(folderIn + 'gspc.csv'))
    for row in reader:
        dateString = '/'.join(row['Date'].split('-'))
        dt = getDateTime(dateString)
        listNum = []
        listNum.append(dt)
        listNum.append(float(row['Open']))
        listNum.append(float(row['Close']))
        spRows.append(listNum)

    #print len(stockRows)

    stockRows.reverse()
    spRows.reverse()

    fid = open('8K_events')
    for event in fid:
        txt += event
    eventList = txt.split('\n')

    for doc in docs:
        # Get time-stamps
        pattern = re.compile('Exhibit [0-9]*.[0-9]*(.*)')
        article = re.findall(pattern,doc)
        pattern = re.compile('TIME:([0-9]*?) ')
        time = re.findall(pattern,doc)[0]
        time = time[0:12]
        # Write the date
        dt = getDateTime(convert2standard(time))
        if (len(article) < 1) or (dt > datetime.datetime(2012,1,1)):
            continue
        out.write('<DOCUMENT>')
        out.write('<DATE>'+dt.strftime("%Y/%m/%d")+'</DATE>')
        # Search for before and after dates
        #print dt
        vec = getEventVector(article[0],eventList) # is a string of binary attributes. file name used here -----
        [dtf,prevPrice,postPrice] = searchForPrev(stockRows,dt)
        [_z,prevSP,postSP] = searchForPrev(spRows,dt)
        [wPrice,mPrice,yPrice] = getWMY(dtf,stockRows)
        #print wPrice
        out.write('<PRICE>'+ str(prevPrice) + ',' + str(postPrice))
        out.write( ',' + str(prevSP) + ',' + str(postSP) + ',' + str(wPrice) + ',' + str(mPrice) + ',' + str(yPrice) +'</PRICE>')
        out.write('<EVENTS>' + vec + '</EVENTS>')
        out.write('<ARTICLE>'+article[0]+'</ARTICLE>')
        out.write('</DOCUMENT>')

    out.close()

def makeDocs(name):
    print 'Solving: ' + name + '\n'
    solve(name)

if __name__ == '__main__':
    if len(sys.argv)>1:
        solve(sys.argv[1])
