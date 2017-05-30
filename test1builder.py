from classifierBuilder import getTree, node, getNodesSorted, getFeatureVector

def doProcess(name,out):
    fd = open(name)
    fid = open(out,"a")

    # Read the data
    txt = ""
    for line in fd:
        txt += line

    n = getTree(txt)[0]
    #print 'Tree built \n'
    nodes = getNodesSorted(n,0)

    #print 'Num nodes', str(len(nodes))

    fnodes = getFeatureVector(nodes)

    l = len(nodes)

    for i in range(l):
        l2 = len(fnodes[0])
        #feature = []
        for j in range(l2):
            fid.write(str(fnodes[i][j]) + ' ')
            #feature.append(fnodes[i][j])
        tmp = 0
        if nodes[i].isContent:
            tmp = 1
        fid.write(str(tmp) + '\n')
        #feature.append(tmp)
        #bigList.append(feature)

    #cPickle.dump(bigList,fid)
    fid.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 2:
        doProcess(sys.argv[1],sys.argv[2])
