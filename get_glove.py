def load_glove_model():
    print('Retrieving glove vectors.')
    fid = open('/home/nikhil/Desktop/seval/glove.6B.50d.txt','r')
    d = {}
    for line in fid:
        splitLine = line.split()
        word = splitLine[0]
        embedding = [float(val) for val in splitLine[1:]]
        d[word] = embedding
    print('Glove vectors retrieved.\n')
    return d

debug = False

if debug:
    d = load_glove_model()
    print d['profit']
