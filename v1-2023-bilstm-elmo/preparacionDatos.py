#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 03:20:05 2024

@author: mluisadiez
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 13:33:24 2024

@author: mluisadiez
"""
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
from tensorflow import keras
from keras import backend as K
from tensorflow.keras.layers import Input, LSTM, Embedding, Dense, TimeDistributed, Dropout, Bidirectional, Lambda, Layer, Concatenate
from tensorflow.keras.models import Sequential, Model
import pandas as pd
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import tensorflow_hub as hub
from tensorflow.keras.layers import add
import numpy as np
import matplotlib.pyplot as plt
import sklearn.metrics as skm




def preparar_datos(tabla):
    
    """print("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
    print(tabla)"""
    
    
    
    """words = list(set(tabla["Word"].values))
    words.append("ENDPAD")
    n_words = len(words); 
    print(n_words)        
    
    tags = list(set(tabla["Tag"].values))
    n_tags = len(tags);
    print(n_tags)
    
    
    class SentenceGetter(object):
    
        def __init__(self, data):
            self.n_sent = 1
            self.data = data
            self.empty = False
            agg_func = lambda s: [(w, p, t) for w, p, t in zip(s["Word"].values.tolist(),
                                                               s["POS"].values.tolist(),
                                                               s["Tag"].values.tolist())]
            self.grouped = self.data.groupby("Sentence #").apply(agg_func)
            self.sentences = [s for s in self.grouped]
    
        def get_next(self):
            try:
                s = self.grouped["Sentence: {}".format(self.n_sent)]
                self.n_sent += 1
                return s
            except:
                return None
        
    getter = SentenceGetter(tabla)
    sentences = getter.sentences
    max_len = 50
    tag2idx = {t: i for i, t in enumerate(tags)}
    
    print("tag to indice")
    print(tag2idx)    
    X = [[w[0] for w in s] for s in sentences]

    new_X = []
    for seq in X:
        new_seq = []
        for i in range(max_len):
            try:
                new_seq.append(str(seq[i]))
            except:
                new_seq.append("__PAD__")
        new_X.append(new_seq)
    X = new_X"""
    
    lista_total_palabras=list()
    lista_total_indices_etiquetas=list()
    
    datos=tabla.to_numpy().transpose().tolist()
    
    X=datos[1]
    y=datos[4]
    
    max_len = 100
    batch_size=31 
    
    
    for w in X:
        
        numadd=100-len(w)
        for i in range(numadd):
            w.append("PADword")
        
    
    
    for i in range(0,len(X)):
         
        for j in range (0,len(X[i])):
            palabra=X[i][j]
            lista_total_palabras.append(palabra)
            
    
    """print(len(set(lista_total_palabras)))"""
    
    for i in range(0,len(y)):
        for j in range (0,len(y[i])):
            indice=y[i][j]
            lista_total_indices_etiquetas.append(int(indice))
            
            
   
    
    n_tags=len(set(lista_total_indices_etiquetas))
    print(n_tags)

    print("LALALALLALLLALLLLALLLA") 
    """print(X)
    print(y)"""
    """y = [[tag2idx[w[2]] for w in s] for s in sentences]"""


    y = pad_sequences(maxlen=max_len, sequences=y, padding="post")

    print(y)
    print("LA YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
    
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.1, random_state=2018)


    """print(len(columna_palabras))"""
    print(X_tr)
    print(len(X_te))

   
    
    print("SQSQSQSQSQSQQSQSQSQQSQSQSQQSQS")
    
   
    elmo_model = hub.Module("https://tfhub.dev/google/elmo/2", trainable=True)
    sess = tf.Session()
    K.set_session(sess)
    sess.run(tf.global_variables_initializer())
    sess.run(tf.tables_initializer())
    
    def ElmoEmbedding(x):
        return elmo_model(inputs={
                            "tokens": tf.squeeze(tf.cast(x, tf.string)),
                            "sequence_len": tf.constant(batch_size*[max_len])
                      },
                      signature="tokens",
                      as_dict=True)["elmo"]
    
    input_text = Input(shape=(max_len,), dtype=tf.string)
    embedding = Lambda(ElmoEmbedding, output_shape=(None, 1024))(input_text)
    x = Bidirectional(LSTM(units=512, return_sequences=True,
                       recurrent_dropout=0.2, dropout=0.2))(embedding)
    x_rnn = Bidirectional(LSTM(units=512, return_sequences=True,
                           recurrent_dropout=0.2, dropout=0.2))(x)
    
    x = add([x, x_rnn])  # residual connection to the first biLSTM
    
    out = TimeDistributed(Dense(n_tags, activation="softmax"))(x)
    model = Model(input_text, out)
    
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    
    
    X_tr, X_val = X_tr[:1213*batch_size], X_tr[-135*batch_size:]
    y_tr, y_val = y_tr[:1213*batch_size], y_tr[-135*batch_size:]
    y_tr = y_tr.reshape(y_tr.shape[0], y_tr.shape[1], 1)
    y_val = y_val.reshape(y_val.shape[0], y_val.shape[1], 1)
    
    print("Las longutudes") 
    print(len(X_tr))
    print(len(y_tr))
    print(len(X_val))
    
    print(len(y_val))
    
    history = model.fit(np.array(X_tr), y_tr, validation_data=(np.array(X_val), y_val),
                    batch_size=batch_size, epochs=5, verbose=1)
    hist = pd.DataFrame(history.history)
    
    plt.figure(figsize=(12,12))
    plt.plot(hist["acc"])
    plt.plot(hist["val_acc"])
    plt.title("Learning curves")
    plt.legend()
    plt.show()
    print(len(X_te))
    i = 0
    a=(np.array(X_te[i:i+batch_size]))
    print(a)
    p = model.predict(np.array(X_te[i:i+batch_size]))[0]
    
    p = np.argmax(p, axis=-1)
    
    lista_true=[]
    lista_pred=[]
    len (p)
    print("{:15} {:5}: ({})".format("Word", "Pred", "True"))
    print("="*30)
    for w, true, pred in zip(X_te[i], y_te[i], p):
        if w != "PADword":
            print("{:15}:{:5} ({})".format(w, pred, true))
    
    
    """print ("FI-score: (:.1%)".format (skm.f1_score(y_te, p)))
    print (skm.classification_report (y_te, p))"""
            
            
            
            