'''
Contains code which helps to visualize word embeddings
To be used as matrix,vector of words

'''
import matplotlib.pyplot as plt
import numpy as np
from sklearn.manifold import TSNE

def plot2D(X,words):
    model = TSNE(num_components=2,random_state=0)
    Y = model.fit_transform(X)

    fig,ax = plt.subplots()
    ax.scatter(Y[:,0],Y[:,1])

    for i,txt in enumerate(words):
        ax.annotate(txt,(Y[i,0],Y[i,1]))

    plt.show()
