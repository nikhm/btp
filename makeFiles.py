import test
import sys

def getNameArray(fileName):
    companies = open(fileName)
    txt = ''
    l = []
    for company in companies:
        txt += company
    l = txt.split('\r\n')
    #l = txt.split('\n')
    #print l
    return l

def makeAll(fileName):
    l = getNameArray(fileName)
    for i in l:
        test.makeDocs(i)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        makeAll(sys.argv[1])
