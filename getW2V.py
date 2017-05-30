import sys

def drawProgressBar(percent, barLen = 20):
    sys.stdout.write("\r")
    progress = ""
    for i in range(barLen):
        if i < int(barLen * percent):
            progress += "="
        else:
            progress += " "
    sys.stdout.write("[ %s ] %.2f%%" % (progress, percent * 100))
    sys.stdout.flush()

def getVectors(words):
    '''
    Return a dict containing word -> vector mapping
    Uses ten passes of the vectors.txt file
    '''
    print 'Obtaing vectors for current run\n'
    fid = open('vectors.txt')
    sz, cnt = 3000000, 0
    w2v = {}
    for line in fid:
        if cnt == 0:
            cnt += 1
            continue
        arr = line.split(' ')
        w = arr[0]
        if w in words:
            vec = [float(x) for x in arr[1:len(arr)-1]]
            w2v[w] = vec
        cnt += 1
        drawProgressBar(float(cnt)/sz)
    return w2v
