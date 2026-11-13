#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 13:33:24 2024

@author: mluisadiez
"""
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import tensorflow as tf
from tensorflow import keras
from keras import backend as K
from tensorflow.keras.layers import Input, LSTM, Embedding, Dense, TimeDistributed, Dropout, Bidirectional, Lambda, Layer, Concatenate
from tensorflow.keras.models import Sequential, Model
import pandas as pd
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import tensorflow_hub as hub
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import add
from tensorflow.keras.layers import LSTM, Embedding, Dense, TimeDistributed, Dropout, Bidirectional, Lambda
import numpy as np
from tensorflow.keras.optimizers.legacy import Adam


def preparar_datos(tabla):
    lista_total_palabras=list()
    lista_total_indices_etiquetas=list()
    
    datos=tabla.to_numpy().transpose().tolist()
    
    columna_palabras=datos[1]
    columna_indices_tag=datos[4]
    
    max_len = 100
    
    
    for w in columna_palabras:
        
        numadd=100-len(w)
        for i in range(numadd):
            w.append("PADword")
        
    
    
    for i in range(0,len(columna_palabras)):
        for j in range (0,len(columna_palabras[i])):
            palabra=columna_palabras[i][j]
            lista_total_palabras.append(palabra)
            
    
    print(len(set(lista_total_palabras)))
    
    for i in range(0,len(columna_indices_tag)):
        for j in range (0,len(columna_indices_tag[i])):
            indice=columna_indices_tag[i][j]
            lista_total_indices_etiquetas.append(int(indice))
    
    n_tags=len(set(lista_total_indices_etiquetas))
    print(n_tags)
    
    y=pad_sequences(maxlen=100,sequences=lista_total_indices_etiquetas[0],padding="post")
    print("LA YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
    
    X_tr,X_te,y_tr,y_te=train_test_split(lista_total_palabras,y,test_size=0.1,random_state=2021)
    """print(len(columna_palabras))
    print(len(X_tr))
    print(len(X_te))"""
  
    ncols=tabla.shape[1]
    batch_size=32
    X_tr,X_val=X_tr[:1213*batch_size],X_tr[-135*batch_size:]
    y_tr,y_val=y_tr[:1213*batch_size],y_tr[-135*batch_size:]
    y_tr=y_tr.reshape(y_tr.shape[0],y_tr.shape[1],1)
    y_val=y_val.reshape(y_val.shape[0],y_val.shape[1],1)
    
    elmo = hub.load("https://tfhub.dev/google/elmo/2").signatures["default"]
    input_text = Input (shape= (max_len,), dtype=tf.string)
    embeddings_list = []
    for sequence in X_tr:
        print(sequence)
        input_tensor = tf.constant(sequence)
        embeddings = elmo(input_tensor)['elmo']
        
        # Extract the tensor from the dictionary and append to the list
        embeddings_list.append(embeddings)
        
    print(embeddings)
    
    """embeddings = elmo(tf.constant(X_tr))["elmo"]"""
    
    x = Bidirectional(LSTM(units=512, return_sequences=True,recurrent_dropout=0.2, dropout=0.2))(embeddings)
    x_rnn = Bidirectional(LSTM(units=512, return_sequences=True,
                           recurrent_dropout=0.2, dropout=0.2))(x)
    """conexion residual al primer biLSTM"""
    x = add([x, x_rnn]) 
    out = TimeDistributed(Dense(n_tags, activation="softmax"))(x)
    
    model = Model(input_text, out)
    """model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    
    history = model.fit(np.array(X_tr), y_tr, validation_data=(np.array(X_val), y_val),
                    batch_size=batch_size, epochs=5, verbose=1)
    print("hola")"""
    
    """x = Bidirectional(LSTM(units=512, return_sequences=True,
                           recurrent_dropout=0.2, dropout=0.2))(embedding)
    x_rnn = Bidirectional(LSTM(units=512, return_sequences=True,
                               recurrent_dropout=0.2, dropout=0.2))(x)
    x = add([x, x_rnn])  # residual connection to the first biLSTM
    out = TimeDistributed(Dense(n_tags, activation="softmax"))(x)"""
    