from textGenerator import txtFromHTML
from bs4 import BeautifulSoup
import time, nltk
from getW2V import getVectors
from dateutil import parser
from datetime import datetime,timedelta
import MySQLdb, string, sys
sys.path.append('../')
import lstm_classifier

'''
This is specific to Reuters business news.
Takes recent news and builds an index of articles. Contains time-stamp as well.
This is dependent on:
    1) txtFromHTML of textGenerator
    2) A classifier on disk -- Currently 'articleClassifier.pkl'
Generates text of corresponding news articles
Needs to be updated from time to time on the basis of change in Reuters source -
Change is to be done in maintainIndex which collects the news articles
'''

#db, cursor = object(), object()

db = MySQLdb.connect('#####','#####','#####','####')
cursor = db.cursor()

# Get the session 'sess' from lstm_classifier.initiailize()
# and use the 'sess' as argument to lstm_classifier.make_predictions
# along with list of sentences (strings)
model_tuple = lstm_classifier.initialize()

def maintainIndex(company):
    debug = False
    searchString = 'http://www.reuters.com/search/news?sortBy=relevance&dateRange=pastDay&blob=' + company
    baseAddress = 'http://www.reuters.com'

    import urllib,re
    resp = urllib.urlopen(searchString)
    txt = resp.read()

    articles = [] # Consists of company, date, headline, date
    # Database should contain following columns:
    # ID  |  Company  |  headline |  articleURL  | dateTime  |  Score

    bs = BeautifulSoup(txt)
    allNews = bs.findAll('div','search-result-content')
    for news in allNews:
        links = news.findAll('a',href=True)
        if len(links) == 0:
            continue
        curURL = baseAddress + links[0]['href']
        dateTime = news.findAll('h5')
        if len(dateTime) == 0:
            continue
        headline = links[0].getText()
        dateTime = dateTime[0].getText()
        dateTime = parser.parse(dateTime)
        articles.append((company,headline,curURL,dateTime))

    # articleLinkAndTime is a list of pairs: (timeStamp, url)
    print 'Number of articles: ', len(articles)

    for article in articles:
        print article
        print('\n')

    return articles

def addToDatabase(articles):
    debug = False
    if (debug):
        return True
    for article in articles:
        # Company | headline | url | dateTime
        company, headline, url, date = article
        date = str(date.year) + '-' + str(date.month) + '-' + str(date.day)
        print date
        if not debug:
            sql = 'INSERT INTO documents (company,headline,url,date) VALUES (%s,%s,%s,%s)'
            try:
                cursor.execute(sql,(company,headline,url,date))
                db.commit()
            except Exception as e:
                #print('Duplicate entry detected!')
                print e
                db.rollback()

def updateScores():
    print 'Updating started!'
    sql = 'SELECT ID,headline FROM documents WHERE score IS NULL'
    cursor.execute(sql)
    entries = cursor.fetchall()
    print 'Received entries'
    id_score_dictionary = {}
    for entry in entries:
        ID = entry[0]
        headline = entry[1]
        predValue = lstm_classifier.make_predictions(model_tuple,[headline])
        # predValue is expected to contain only one length array
        if len(predValue) == 0:
            print 'Length is zero of predValue'
            continue
        predValue = predValue[0]
        #print('ID: %d, headline: %s, predValue:%f'%(ID,headline,predValue))
        id_score_dictionary[ID] = predValue
    for entry in id_score_dictionary.iteritems():
        print entry[1],entry[0]
        sql = 'UPDATE documents SET score=%s WHERE ID = %s'
        try:
            id_var = entry[0]
            score_var = entry[1]
            cursor.execute(sql,(score_var,id_var))
            db.commit()
        except Exception as e:
            print e
            db.rollback()
    print 'Bye'

if __name__ == '__main__':
    #initiailize()
    companies = ['google','yahoo','microsoft','facebook','merck','citigroup']
    numMinutes = 10
    try:
        currentTime = datetime.now()
        while True:
            for company in companies:
                articles = maintainIndex(company)
                addToDatabase(articles)
            timeToSleep = (currentTime +  timedelta(0,60*numMinutes)) - datetime.now()
            timeToSleep = timeToSleep.seconds
            print timeToSleep
            updateScores()
            if timeToSleep > 0:
                time.sleep(timeToSleep)
    except KeyboardInterrupt:
        pass
    print 'Exiting...'
