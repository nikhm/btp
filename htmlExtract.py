stopWords = set()

def setStopWords():
    stopWords.add('and')
    stopWords.add('the')
    stopWords.add('a')
    stopWords.add('an')
    stopWords.add('are')
    stopWords.add('as')
    stopWords.add('for')
    stopWords.add('was')
    stopWords.add('is')
    stopWords.add('of')
    stopWords.add('to')
    stopWords.add('will')
    stopWords.add('he')
    stopWords.add('she')

class node(object):
    def __init__(self):
        self.children, self.directText = [], ""
        self.textDensity, self.numTags, self.numChars, self.numWords = \
            -1.0,-1,-1,-1
        self.isContent, self.isBody, self.parent = False, False, None

    def addChild(self,other):
        self.children.append(other)
        other.parent = self
        return

    def getNumChars(self):
        if self.numChars != -1:
            return self.numChars
        numChars = len(self.directText)
        l = len(self.children)
        for i in range(l):
            numChars += self.children[i].getNumChars()
        self.numChars = numChars
        return numChars

    def getNumTags(self):
        if self.numTags != -1:
            return self.numTags
        l = len(self.children)
        numTags = l
        for i in range(l):
            numTags += self.children[i].getNumTags()
        self.numTags = numTags
        return numTags

    def getNumWords(self):
        if self.numWords != -1:
            return self.numWords
        l = len(self.directText)
        numWords = 0
        for i in range(l):
            if (self.directText == '.') or (self.directText == ' '):
                numWords += 1
            if (self.directText == '!') or (self.directText == ','):
                numWords += 1
        self.numWords = numWords
        return numWords

    def getModifiedTextDensity(self):
        lines = 1.0 + ((self.getTextDensity())/80.0)
        ans = self.getNumWords()/lines
        return ans

    def getTextDensity(self):
        if self.textDensity != -1:
            return self.textDensity
        numTags = self.getNumTags()
        numChars = self.getNumChars()
        if (numTags != 0):
            textDensity = (1.0*numChars)/numTags
        else:
            textDensity = (1.0*numChars)
        self.textDensity = textDensity
        return textDensity;

def getFeatureVector(nodeList):
    '''
    This method returns a feature vector for each node in nodeList
    Each node associated with -
    1) Text density
    2) Modified Text Density
    3) Parent Node text density
    4) Child node text density average
    5) Number of direct children
    The below two have been extracted from in order traversal of nodes
     6) Left node text density
     7) Right node text density
    8) Number of full stops
    '''
    featureNodes = []
    nodeLength = len(nodeList)
    for j in range(nodeLength):
        n = nodeList[j]
        feature = []
        feature.append(n.getTextDensity())
        feature.append(n.getModifiedTextDensity())
        if(n.parent != None):
            feature.append(n.parent.getTextDensity())
        else:
            feature.append(0.0)
        l = len(n.children)
        avg = 0.0
        for i in range(l):
            avg += (1.0*n.children[i].getTextDensity())
        if(l != 0):
            avg /= l
        feature.append(avg)
        feature.append(l)
        if(j != 0):
            feature.append(nodeList[j-1].getTextDensity())
        else:
            feature.append(0.0)
        if(j != (nodeLength-1)):
            feature.append(nodeList[j+1].getTextDensity())
        else:
            feature.append(0.0)
        l = len(n.directText)
        cnt = 0
        for i in range(l):
            if n.directText[i] == '.':
                cnt += 1
        feature.append(cnt)

        featureNodes.append(feature)
    return featureNodes

def getNodesSorted(head,method):
    from collections import deque
    q = deque()
    q.append(head)
    nodeList = []
    maxDensity, tmp = -1, None
    while (len(q) != 0):
        n = q.popleft()
        if (maxDensity < n.getTextDensity()):
            maxDensity = n.getTextDensity
            tmp = n
        if ((n.about.find("style") == -1) and (n.about.find("script") == -1) and (n.about.find("!--") == -1)):
            nodeList.append(n)
        l = len(n.children)
        for i in range(l):
            q.append(n.children[i])

    return nodeList
    # If the classifier is ready discard below and return nodeList
'''
    minDensity = maxDensity
    foundBody = False
    while (tmp is not None):
        minDensity = min(minDensity,tmp.getTextDensity())
        if (tmp.parent is not None) and (tmp.parent.isBody):
            foundBody = True
            break
        tmp = tmp.parent
    if (method == 0):
        if (foundBody == False):
            l = len(nodeList)
            for i in range(l):
                if (nodeList[i].getTextDensity() >= minDensity):
                    nodeList[i].isContent = True
        else:
            q = deque()
            q.push(tmp)
            while (len(q) != 0):
                n = q.popleft()
                if (n.getTextDensity() >= minDensity):
                    n.isContent = True
                l = len(n.children)
                for i in range(l):
                    q.push(n.children[i])
    elif (method == 1):
        print ''
    return nodeList
'''
def getTree(s):
    '''
    Returns DOM tree for HTML string
    '''
    l = len(s)
    st, curString, headers, isFirst = [], [], [], False
    i = -1
    while (i<l-1):
        i += 1
        if (s[i] == '<'):
            if (s[i+1] != '/'):
                # Check for unpaired tags in HTML and let go of them
                n = node()
                tmp = None
                if (len(st) != 0):
                    tmp = st[len(st) - 1]
                else:
                    isFirst = True
                if (tmp is not None):
                    tmp.addChild(n)
                    n.parent = tmp
                st.append(n)
                curString.append("")
                about, i = "", i+1
                z = i
                while (s[i] != '>'):
                    about += s[i]
                    i += 1
                n.about = about
                if (len(about) >= 4) and (about[0:4] == 'body'):
                    n.isBody = True
                if (len(about) >= 6) and (about[0:6] == 'script'):
                    st.pop(); curString.pop();
                    flag = True
                    while flag:
                        if s[i:i+9] == "</script>":
                            i += 8
                            break
                        i += 1
                    continue
                if (isFirst):
                    headers.append(n)
                    isFirst = False

                if s[i-1] == '/':
                    st.pop(); curString.pop()
                    continue

                # Void elements. Being careful
                if ((z+4 < l) and (s[z:z+4] == "area")) or ((z+4 < l) and (s[z:z+4] == "base")) or ((z+4 < l) and (s[z:z+4] == "link"))\
                    or ((z+4 < l) and (s[z:z+4] == "meta")) or ((z+3 < l) and (s[z:z+3] == "col"))\
                        or ((z+2 < l) and (s[z:z+2] == "br")) or ((z+5 < l) and (s[z:z+5] == "input")) or ((z+5 < l) and (s[z:z+5] == "param"))\
                            or ((z+7 < l) and (s[z:z+7] == "command")) or ((z+6 < l) and (s[z:z+6] == "keygen"))\
                                or ((z+6 < l) and (s[z:z+6] == "source")) or ((z+2 < l) and (s[z:z+2] == "hr")) or ((z+3 < l) and (s[z:z+3] == "img")):
                    st.pop(); curString.pop()

            else:
                while (s[i] != '>'):
                    i += 1
                tmp = st[len(st)-1]
                tmp.directText = curString[len(curString)-1]
                st.pop(); curString.pop()
        else:
            if (len(curString) == 0):
                continue
            sTmp = curString[len(curString)-1]; curString.pop()
            sTmp += s[i]; curString.append(sTmp)
    return headers

'''
Void elements in HTML: area, base, br, col, hr, img, input, link, meta, param, command, keygen, source
'''
