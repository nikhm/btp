def getList(name):
    fid = open(name)
    content = fid.readlines()
    content = [x.strip('\n') for x in content]
    content = [x for x in content if x!='']
    content = [map(float,x.split(' ')) for x in content]

    fid.close()
    fid.open('articleClassifier.pkl','wb')
    import cPickle
    cPickle.dump(content,fid)
    fid.close()

if __name__ == '__main__':
    import sys
    if(len(sys.argv) > 1):
        getList(sys.argv[1])
