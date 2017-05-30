'''
Text Generator (from HTML)
Going the function way. Call txtFromHTML:

Given a link and classifier txtFromHTML returns a string containing possible
content. It uses doProcess which takes in HTML string and classifier name on
disk.

doProcess is dependent on:
    1) getTree -- HTML parser giving a DOM Tree
    2) node    -- to represent each tag in HTML in DOM Tree
    3) getNodesSorted and getFeatureVector: give a list of nodes in DOM tree and
       their corresponding feature vectors
________________________________________________________________________________
Going the main program way:

Useful for testing purposes.
Arguments are text file containing HTML text and classifier name

'''

from htmlExtract import getTree, node, getNodesSorted, getFeatureVector

def doProcess(htmlTxt,classifier):
    debug = True
    vec = getTree(htmlTxt)

    if(len(vec) < 1):
        print 'Error'
        return
        #exit()
    n = vec[0]
    #print 'Tree built \n'
    nodes = getNodesSorted(n,0)

    fnodes = getFeatureVector(nodes)

    # Next part of method includes using above feature vectors to classify
    # each of the blocks
    import cPickle
    fid = open(classifier)
    forest = cPickle.load(fid)
    isContent = forest.predict(fnodes)

    #print isContent

    cnt = 0
    for tmp in nodes:
        if(isContent[cnt] == 1):
            tmp.isContent = True
        cnt += 1

    out = ""
    for tmp in nodes:
        if tmp.isContent:
            if tmp.directText != "":
                out += (tmp.directText + '\n')
    #print fnodes[len(nodes)/2]

    l = len(out)

    out = out.replace('\n',' ')
    out = out.replace('\r',' ')

    cur = out[0]

    for i in range(1,l):
        if (((out[i] == ' ' ) and (out[i-1] == ' ')) == False):
            cur += out[i]

    return cur

def txtFromHTML(html,classifier):
    import urllib
    resp = urllib.urlopen(html)
    htmlTxt = resp.read()
    txt = doProcess(htmlTxt,classifier)
    return txt

if __name__ == '__main__':
    '''
    To be used as python textGenerator.py html.txt articleClassifier.pkl
    '''
    import sys
    if len(sys.argv) > 2:
        fid = open(sys.argv[1])
        txt = ''
        for line in fid:
            txt += line
        txt = doProcess(txt,sys.argv[2])
        print txt
