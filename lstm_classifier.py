'''
This script is to be used for directly classifying
'''

import os,sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from tensorflow.contrib import rnn
import json
from nltk.stem.porter import PorterStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords
import re, string, json, cPickle
from sklearn import svm
import numpy as np

from get_glove import load_glove_model

d = load_glove_model()

def process_headline(headline,not_unicode=True,num_steps=10,num_dims=50,reverse=False):
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
    vec, cnt = [], 0
    for word in words:
        if word in d:
            vec.append(d[word])
    cnt = len(vec)
    while cnt < num_steps:
        vec.append([0]*num_dims)
        cnt += 1
    # vec is 10 x 50 list
    return vec

class Model():
    def __init__(self,state_size):
        self.state_size = state_size
    def __call__(self,inputs_f,inputs_b,batch_size,num_steps,num_dims):
        # inputs -> [batch_size , num_steps , num_dims]

        inputs_f = tf.transpose(inputs_f,[1,0,2])
        inputs_b = tf.transpose(inputs_b,[1,0,2])

        with tf.variable_scope('forward'):
            cell_f = rnn.DropoutWrapper(rnn.BasicLSTMCell(self.state_size),1.0,1.0)
            initial_state = cell_f.zero_state(batch_size, tf.float32)
            outputs_f = []
            state = initial_state
            for time_step in range(num_steps):
                if time_step > 0:
                    tf.get_variable_scope().reuse_variables()
                cell_output, state = cell_f(inputs_f[time_step, :, :], state)
                outputs_f.append(cell_output)

        with tf.variable_scope('backward'):
            cell_b = rnn.DropoutWrapper(rnn.BasicLSTMCell(self.state_size),1.0,1.0)
            initial_state = cell_b.zero_state(batch_size, tf.float32)
            outputs_b = []
            state = initial_state
            for time_step in range(num_steps):
                if time_step > 0:
                    tf.get_variable_scope().reuse_variables()
                cell_output, state = cell_b(inputs_b[time_step, :, :], state)
                outputs_b.append(cell_output)

        # Attention model

        hidden_size = 8
        W_w = tf.get_variable(shape=[self.state_size*2,hidden_size],name='weights_w',initializer=tf.random_normal_initializer())
        b_w = tf.get_variable(shape=[1,hidden_size],name='bias_w',initializer=tf.random_normal_initializer())
        u_w_t = tf.get_variable(shape=[hidden_size,1],name='attention',initializer=tf.random_normal_initializer()) # Transpose is directly taken

        # Output calculation  *(num_classes -> 1)
        W_s = tf.get_variable(shape=[self.state_size*2,1],name='weights_s',initializer=tf.random_normal_initializer())
        b_s = tf.get_variable(shape=[1,1],name='bias_s',initializer=tf.random_normal_initializer())

        #tf.get_variable_scope().reuse_variables()
        outputs = []
        for time_step in range(num_steps):
            #tf.get_variable_scope().reuse_variables()
            o = tf.concat([outputs_f[time_step],outputs_b[time_step]],axis=1)
            out = tf.tanh( tf.matmul(o,W_w) + b_w )
            #print(outputs_f[time_step],o,out)
            outputs.append(out)
        # Computing alphas
        alphas = []
        #alphas.append( tf.exp( tf.matmul( out[0],u_w_t ) ) )
        for i in range(num_steps):
            #tf.get_variable_scope().reuse_variables()
            #print(outputs[i],u_w_t)
            alpha_i = tf.exp( tf.matmul( outputs[i],u_w_t ) )
            alphas.append(alpha_i)
        sum_alphas = alphas[0]
        for i in range(1,num_steps):
            sum_alphas = sum_alphas + alphas[i]
        for i in range(num_steps):
            alphas[i] = alphas[i]/sum_alphas

        # Computing outputs
        y_arr = []
        for time_step in range(num_steps):
            #tf.get_variable_scope().reuse_variables()
            o = tf.concat([outputs_f[time_step],outputs_b[time_step]],axis=1)
            y_i = tf.matmul(o,W_s) + b_s
            y_arr.append(y_i)

        y = alphas[0]*y_arr[0]
        for i in range(1,num_steps):
            y = y + alphas[i]*y_arr[i]
        #Use the y for either classification or regression task
        return y

def initialize():
    # Hyperparameters
    int_batch_size = 1
    state_size = 4
    num_dims = 50
    num_steps = 10

    # Describe the model and input,output placeholders
    batch_size = tf.placeholder(dtype=tf.int32)
    inputs_f = tf.placeholder(shape=[None,num_steps,num_dims],dtype=tf.float32)
    inputs_b = tf.placeholder(shape=[None,num_steps,num_dims],dtype=tf.float32)
    output_placeholder = tf.placeholder(shape=[None,1],dtype=tf.float32)

    print('Building model!')
    model = Model(state_size)
    output = model(inputs_f,inputs_b,batch_size=batch_size,num_dims=num_dims,num_steps=num_steps)
    print('Model built!')

    pred = output

    # Below terms are not required and may be removed altogether when using the classifier
    # Addition
    #tv = tf.trainable_variables()
    #regularization_cost = tf.reduce_sum([ tf.nn.l2_loss(v) for v in tv if 'bias' not in v.name])*0.01

    #loss = tf.reduce_mean(tf.square(pred-output_placeholder))
    #train = tf.train.AdamOptimizer(0.0005).minimize(loss)

    init = tf.global_variables_initializer()
    sess = tf.Session()
    saver = tf.train.Saver()
    sess.run(init)
    folder_name = '/home/nikhil/Desktop/seval/saved_models/'
    saver.restore(sess,folder_name + 'lstm_' + str(state_size) + '.ckpt')
    return (batch_size,inputs_f,inputs_b,pred,sess)

# Below method takes in session 'sess' and sentences to return a list of scores
def make_predictions(model_tuple,sentences):
    # Moved to initialize()
    # Hyperparameters
    int_batch_size = 1
    state_size = 4
    num_dims = 50
    num_steps = 10
    batch_size,inputs_f,inputs_b,pred,sess = model_tuple
    predictions = []
    for sentence in sentences:
        x,x_r = np.array([process_headline(sentence,reverse=False)]), np.array([process_headline(sentence,reverse=True)])
        predValues = sess.run([pred],feed_dict={batch_size:int_batch_size,inputs_f:x,inputs_b:x_r})
        predValues = predValues[0]
        predictions.append(predValues[0][0])
    return predictions

if __name__ == '__main__':
    sentences = ['']*11
    sentences[0] = 'Yahoo! shares continue to slide'
    sentences[1] = 'Holiday discounts may hurt apparel store profits'
    sentences[2] = 'Marsh could get good price for Putnam: WSJ'
    sentences[3] = 'Dollar weakness poses growth risk: OECD chief'
    sentences[4] = 'U.S. auto sales slowing say forecasts: report'
    sentences[5] = 'Swift rejects $2.2bln buyout offer, stock rises'
    sentences[6] = 'Falling dollar may benefit some firms'
    sentences[7] = 'Monster expands newspaper alliances for job ads'
    sentences[8] = '''Google parent Alphabet's revenue rises 22.2 percent'''
    sentences[9] = 'Microsoft to offer movies, TV shows on game service'
    sentences[10] = 'Barclays share price: Investment bank to shrink further despite CEO exit'
    model_tuple = initialize()
    predValues = make_predictions(model_tuple,sentences)
    lt = len(predValues)
    for i in range(lt):
        print('_________________________________________________________')
        print sentences[i]
        print predValues[i]
