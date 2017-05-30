import json
from nltk.stem.porter import PorterStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords
import re, string

def get_embedding(vocab_length):
    base_folder = 'seval_data/'
    files = [base_folder + 'Headlines_Testdata.json',base_folder + 'Headline_Trainingdata.json',base_folder +'Headline_Trialdata.json']
    txt = ''
    pat = re.compile('[a-z]')
    stop = set(stopwords.words('english')) - set('not')
    for record in files:
        fid = open(record)
        data_array = json.load(fid)
        fid.close()
        for data in data_array:
            tmp = data['title'].encode('ascii','ignore') + ' '
            if not (tmp == '' or tmp == ' '):
                txt += tmp
    txt = word_tokenize(txt)
    stemmer = PorterStemmer()
    words = []
    for word in txt:
        tmp = word.lower().translate(None,string.punctuation)
        if len(re.findall(pat,tmp)) != len(tmp):
            continue
        if word.lower() not in stop:
            words.append(stemmer.stem(tmp))
    words.sort()
    #print words
    freq_words = []
    index, lt, current_count = 1, len(words), 1
    while index < lt:
        if words[index] != words[index-1]:
            freq_words.append( (current_count,words[index-1]) )
            current_count = 1
        else:
            current_count += 1
        index += 1
    freq_words.sort()
    freq_words = freq_words[::-1]
    freq_words = freq_words[:vocab_length]
    #print freq_words
    #print 'First few words: \n\n'
    w2e = {}
    e2w = {}
    for i in range(vocab_length):
        w2e[i] = freq_words[i][1]
        e2w[freq_words[i][1]] = i
    return (w2e,e2w)


debug = False

if debug:
    w2e,e2w = get_embedding(100)
    print w2e
    print e2w
