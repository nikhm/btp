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
from embedding_functions import get_embedding

#vocab_length = 500
#w2e,e2w = get_embedding(vocab_length)
#print w2e
#stemmer = PorterStemmer()
d = load_glove_model()

def get_accuracy(predicted,actual):
    # Of size (batch_size,num_classes)
    lt = len(predicted)
    p_class = [predicted[i]>0 for i in range(lt)]
    a_class = [actual[i]>0 for i in range(lt)]
    c = [p_class[i]==a_class[i] for i in range(lt)]
    correct_percent = np.sum(c).astype(np.float32)/lt
    #print correct_percent
    return correct_percent

def drawProgress(lossValue,accuracy):
    # d represents distribution of training data
    sys.stdout.write("\r")
    sys.stdout.write("Loss : %0.2f, batch_accuracy : %0.2f" % (lossValue,accuracy))
    sys.stdout.flush()

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
            cell_f = rnn.DropoutWrapper(rnn.BasicLSTMCell(self.state_size),1.0,0.8)
            initial_state = cell_f.zero_state(batch_size, tf.float32)
            outputs_f = []
            state = initial_state
            for time_step in range(num_steps):
                if time_step > 0:
                    tf.get_variable_scope().reuse_variables()
                cell_output, state = cell_f(inputs_f[time_step, :, :], state)
                outputs_f.append(cell_output)

        with tf.variable_scope('backward'):
            cell_b = rnn.DropoutWrapper(rnn.BasicLSTMCell(self.state_size),1.0,0.8)
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
        W_w = tf.get_variable(shape=[self.state_size*2,hidden_size],name='weights_w',initializer=tf.contrib.layers.xavier_initializer(uniform=True, seed=None, dtype=tf.float32))
        b_w = tf.get_variable(shape=[1,hidden_size],name='bias_w',initializer=tf.contrib.layers.xavier_initializer(uniform=True, seed=None, dtype=tf.float32))
        u_w_t = tf.get_variable(shape=[hidden_size,1],name='attention',initializer=tf.contrib.layers.xavier_initializer(uniform=True, seed=None, dtype=tf.float32)) # Transpose is directly taken

        # Output calculation  *(num_classes -> 1)
        W_s = tf.get_variable(shape=[self.state_size*2,1],name='weights_s',initializer=tf.contrib.layers.xavier_initializer(uniform=True, seed=None, dtype=tf.float32))
        b_s = tf.get_variable(shape=[1,1],name='bias_s',initializer=tf.contrib.layers.xavier_initializer(uniform=True, seed=None, dtype=tf.float32))
        #tf.random_normal_initializer()

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



def main():
    # Hyperparameters
    int_batch_size = 32
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

    # Addition
    tv = tf.trainable_variables()
    regularization_cost = tf.reduce_sum([ tf.nn.l2_loss(v) for v in tv if 'bias' not in v.name])*0.005

    loss = tf.reduce_mean(tf.abs(pred-output_placeholder)) + regularization_cost
    train = tf.train.AdamOptimizer(0.001).minimize(loss)

    init = tf.global_variables_initializer()
    sess = tf.Session()
    saver = tf.train.Saver()
    sess.run(init)

    # Take training inputs

    train_file = 'seval_data/Headline_Trainingdata.json'

    fid = open(train_file)
    data_array = json.load(fid)

    dl = len(data_array)

    train_length = int(0.8*dl)

    X, X_rev, y = [], [], []
    for i in range(train_length):
        data = data_array[i]
        #print data
        heading = data['title']
        sentiment = data['sentiment']
        x_,x_rev, y_ = process_headline(heading,not_unicode=False), process_headline(heading,not_unicode=False,reverse=True), float(sentiment)
        X.append(x_)
        X_rev.append(x_rev)
        y.append([y_])

    num_batches = train_length/int_batch_size

    X_batches, X_rev_batches, y_batches = [], [], []
    for i in range(num_batches):
        X_mini_batch = X[(i*int_batch_size):(i+1)*int_batch_size] # [batch_size x time_step x num_dims]
        X_rev_mini_batch = X_rev[(i*int_batch_size):(i+1)*int_batch_size]
        y_mini_batch = y[(i*int_batch_size):(i+1)*int_batch_size] # [batch_size x 1 ]
        X_batches.append(np.array(X_mini_batch))
        X_rev_batches.append(np.array(X_rev_mini_batch))
        y_batches.append(np.array(y_mini_batch))

    num_epochs = 350
    print('Training started:\n')
    for epoch in range(num_epochs):
        accuracy = []
        for i in range(num_batches):
            # Paste 1)
            _,lossValue,predValues = sess.run([train,loss,pred],feed_dict={batch_size:int_batch_size,inputs_f:X_batches[i],inputs_b:X_rev_batches[i],output_placeholder:y_batches[i]})
            current_accuracy = get_accuracy(predValues,y_batches[i])
            accuracy.append(current_accuracy)
            drawProgress(lossValue,current_accuracy*100)
        print(' Accuracy: %0.2f'%(sum(accuracy)*100/num_batches))
    print('\nEnd of training!')



    int_batch_size = 1

    print('Testing the model')

    X, X_rev, y = [], [], []
    for i in range(train_length,dl):
        data = data_array[i]
        #print data
        heading = data['title']
        #print heading
        sentiment = data['sentiment']
        x_,x_rev, y_ = process_headline(heading,not_unicode=False), process_headline(heading,not_unicode=False,reverse=True), float(sentiment)
        X.append(x_)
        X_rev.append(x_rev)
        y.append([y_])

    num_batches = (dl-train_length)/int_batch_size

    X_batches, X_rev_batches, y_batches = [], [], []
    for i in range(num_batches):
        X_mini_batch = X[(i*int_batch_size):(i+1)*int_batch_size] # [batch_size x time_step x num_dims]
        X_rev_mini_batch = X_rev[(i*int_batch_size):(i+1)*int_batch_size]
        y_mini_batch = y[(i*int_batch_size):(i+1)*int_batch_size] # [batch_size x 1 ]
        X_batches.append(np.array(X_mini_batch))
        X_rev_batches.append(np.array(X_rev_mini_batch))
        y_batches.append(np.array(y_mini_batch))

    final_accuracy = 0.0
    averageLoss = 0.0
    for epoch in range(1):
        accuracy, predictions = [], []
        for i in range(num_batches):
            lossValue,predValues = sess.run([loss,pred],feed_dict={batch_size:int_batch_size,inputs_f:X_batches[i],inputs_b:X_rev_batches[i],output_placeholder:y_batches[i]})
            current_accuracy = get_accuracy(predValues,y_batches[i])
            averageLoss += np.sum( np.abs( predValues - y_batches[i] ) )
            print data_array[i+train_length]['title']
            print('actual:%f , predicted: %f'%(data_array[i+train_length]['sentiment'],predValues[0][0]))
            # 2)
            accuracy.append(current_accuracy)
            #drawProgress(lossValue,current_accuracy*100)
        final_accuracy = sum(accuracy)*100/num_batches
        averageLoss /= num_batches
        print('Accuracy: %0.2f, Loss: %0.2f'%(final_accuracy,averageLoss))
    print('\nEnd of Testing!')

    print('\n')
    save_model = input('Do you want to save the model?(1/0)  ')

    if save_model:
        save_path = saver.save(sess,'saved_models/lstm_' + str(state_size) + '.ckpt')
        print("Model saved in file: %s" % save_path)

if __name__ == '__main__':
    main()
    print('')

# Some pasting stuff
'''
1)
if (epoch == 0 and i == 0):
    print 'Vector 1:'
    print X_batches[i]
    print type(X_batches[i])
    print 'Vector 2:'
    print X_rev_batches[i]
    print type(X_rev_batches[i])
    print 'Output: '
    print y_batches[i]
    print type(y_batches[i])

2)
for j in range(int_batch_size):
    predictions.append( (predValues[j][0],y_batches[i][j][0]) )

'''
