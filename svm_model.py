import json
from nltk.stem.porter import PorterStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords
import re, string, json, cPickle
from sklearn import svm
import numpy as np

from get_glove import load_glove_model
from embedding_functions import get_embedding

vocab_length = 400
w2e,e2w = get_embedding(vocab_length)
#print w2e
stemmer = PorterStemmer()

d = load_glove_model()

def process_headline_2(headline,not_unicode=True,num_steps=10,num_dims=50,reverse=False):
    '''
    Returns a 50 dimensional feature
    '''
    pat = re.compile('[a-z]')
    stop = set(stopwords.words('english')) - set('not')
    if not_unicode:
        tmp = headline
    else:
        tmp = headline.encode('ascii','ignore')
    txt = word_tokenize(tmp)
    words = []
    for word in txt:
        tmp = word.lower().translate(None,string.punctuation)
        if len(re.findall(pat,tmp)) != len(tmp):
            continue
        if word.lower() not in stop:
            #words.append(stemmer.stem(tmp))
            words.append(tmp)
    #print words
    '''
    vec = [0.0]*vocab_length
    for word in words:
        #print 'Lama!'
        if word in e2w:
            #print w2e[word]
            vec[e2w[word]] = 1.0
    '''
    words = words[:num_steps]
    if reverse:
        words = words[::-1]
    #vec, cnt = [], 0
    vec = np.array([0]*50)
    for word in words:
        if word in d:
            vec = vec + np.array(d[word])
    # vec is  list
    return vec

def process_headline(headline,not_unicode=True):
    '''
    Returns a vocab_length size list representing presence/absence of words
    '''
    pat = re.compile('[a-z]')
    stop = set(stopwords.words('english')) - set('not')
    if not_unicode:
        tmp = headline
    else:
        tmp = headline.encode('ascii','ignore')
    txt = word_tokenize(tmp)
    words = []
    for word in txt:
        tmp = word.lower().translate(None,string.punctuation)
        if len(re.findall(pat,tmp)) != len(tmp):
            continue
        if word.lower() not in stop:
            words.append(stemmer.stem(tmp))
    #print words
    vec = [0.0]*vocab_length
    for word in words:
        #print 'Lama!'
        if word in e2w:
            #print w2e[word]
            vec[e2w[word]] = 1.0
    return vec

def main():
    train_file = 'seval_data/Headline_Trainingdata.json'

    fid = open(train_file)
    data_array = json.load(fid)

    dl = len(data_array)

    train_length = int(0.8*dl)

    X, y = [], []
    for i in range(train_length):
        data = data_array[i]
        #print data
        heading = data['title']
        sentiment = data['sentiment']
        x_,y_ = process_headline_2(heading,False), float(sentiment)
        X.append(x_)
        y.append(y_)

    #print X[0]
    #print y[0]
    clf = svm.SVR()
    clf.fit(X,y) # Here X - [n_samples,n_features], y - [n_samples]

    Xt, yt = [], []
    for i in range(train_length,dl):
        data = data_array[i]
        heading = data['title']
        sentiment = data['sentiment']
        x_,y_ = process_headline_2(heading,False), float(sentiment)
        Xt.append(x_)
        yt.append(y_)

    y_pred = np.array(clf.predict(Xt))
    yt = np.array(yt)
    #print y_pred
    print np.sum( (y_pred*yt) > 0 )/float(dl-train_length)
    print np.sum( np.abs((y_pred-yt)) )/float(dl-train_length)

    # save the classifier
    with open('headline_svm_classifier.pkl', 'wb') as fid:
        cPickle.dump(clf, fid)

if __name__ == '__main__':
    main()
