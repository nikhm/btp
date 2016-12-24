import nltk
from nltk.corpus import stopwords
from nltk.tag import pos_tag,map_tag
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet

#lmtzr = WordNetLemmatizer()

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('ADJ'):
        return wordnet.ADJ
    elif treebank_tag.startswith('VERB'):
        return wordnet.VERB
    elif treebank_tag.startswith('NOUN'):
        return wordnet.NOUN
    elif treebank_tag.startswith('ADV'):
        return wordnet.ADV
    else:
        return None

def customLemmatize(sentence,lmtzr):
    #sentence = "I am not going to the party!"

    sentence = nltk.word_tokenize(sentence)
    stop = set(stopwords.words('english'))

    posTagged = pos_tag(sentence)
    #print posTagged

    dummy = [map_tag('en-ptb','universal',tag) for word,tag in posTagged]
    #print dummy

    pos_tags = [get_wordnet_pos(x) for x in dummy]

    #print pos_tags

    l = len(sentence)
    words = []
    for i in range(l):
        if (pos_tags[i] is not None) and ((sentence[i] not in stop) or (sentence[i] == 'not')):
            words.append((sentence[i],pos_tags[i]))

    #print words

    #sentence = [lmtzr.lemmatize(x[0],x[1]) for x in words]
    sentence = [lmtzr(x[0],x[1]) for x in words]

    #print sentence
    return sentence
