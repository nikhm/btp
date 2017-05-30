def buildClassifier(name):
    import cPickle
    from sklearn.ensemble import RandomForestClassifier

    content = cPickle.load(open(name))

    if(len(content) == 0):
        exit()

    X, y = [], []
    numFeatures = len(content[0]) - 1
    # Includes last one as decision
    for entry in content:
        X.append(entry[:numFeatures])
        y.append(entry[numFeatures])

    forest = RandomForestClassifier(n_estimators=60,max_features="log2",max_depth=10)
    forest.fit(X,y)
    print forest.score(X,y)
    fid = open('articleClassifier.pkl','wb')
    cPickle.dump(forest,fid)
    fid.close()

    return

if __name__ == '__main__':
    '''
    To be used as buildFromTxt.py data.pkl
    where data.pkl is supposed to contain a list
    '''
    import sys
    if(len(sys.argv) > 1):
        buildClassifier(sys.argv[1])
