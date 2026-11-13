#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 04:06:40 2024

@author: mluisadiez
"""

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import add
from tensorflow.keras.layers import LSTM, Embedding, Dense, TimeDistributed, Dropout, Bidirectional, Lambda
import numpy as np
from tensorflow.keras.optimizers.legacy import Adam
import torch
from transformers import BertTokenizer, BertForTokenClassification
from transformers import AdamW, get_linear_schedule_with_warmup
from torch.utils.data import DataLoader
from keras import layers
X = [[w[0] for w in s] for s in sentences]

new_X = []
for seq in X:
    new_seq = []
    for i in range(max_len):
        try:
            new_seq.append(seq[i])
        except:
            new_seq.append("__PAD__")
    new_X.append(new_seq)
X = new_X

print(X[1])

y = [[tag2idx[w[2]] for w in s] for s in sentences]


y = pad_sequences(maxlen=max_len, sequences=y, padding="post", value=tag2idx["O"])

print(y[1])
print("LA YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.1, random_state=2018)


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
x = Bidirectional(LSTM(units=512, return_sequences=True,
                       recurrent_dropout=0.2, dropout=0.2))(embeddings_list)
x_rnn = Bidirectional(LSTM(units=512, return_sequences=True,
                           recurrent_dropout=0.2, dropout=0.2))(x)
x = add([x, x_rnn])  # residual connection to the first biLSTM
out = TimeDistributed(Dense(n_tags, activation="softmax"))(x)

model = Model(input_text, out)

model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

history = model.fit(np.array(X_tr), y_tr, validation_data=(np.array(X_val), y_val),
                batch_size=batch_size, epochs=5, verbose=1)

hist = pd.DataFrame(history.history)
