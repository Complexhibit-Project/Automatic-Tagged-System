#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 07:51:13 2024

@author: mluisadiez
"""

import tensorflow as tf
from tensorflow import keras
from keras import backend as K
from tensorflow.keras.layers import Input, LSTM, Embedding, Dense, TimeDistributed, Dropout, Bidirectional, Lambda, Layer, Concatenate
from tensorflow.keras.models import Sequential, Model
import pandas as pd
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import tensorflow_hub as hub

elmo_model_path = "https://tfhub.dev/google/elmo/3"
elmo_layer = hub.KerasLayer(elmo_model_path, input_shape=[], dtype=tf.string, trainable=False)

model = tf.keras.Sequential([
    elmo_layer,
    tf.keras.layers.Dense(8, activation='sigmoid'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

# Setting hyperparameter  
optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)
model.compile(loss='binary_crossentropy',optimizer=optimizer,metrics=['accuracy'])

# Model Summary
model.summary()

#Data
data = ['our deeds reason earthquake may allah forgive us', 'forest fire near la ronge sask canada', 'all residents asked shelter place notified officers no evacuation shelter place orders expected', ' people receive wildfires evacuation orders california', 'just got sent photo ruby alaska smoke wildfires pours school', 'rockyfire update  california hwy  closed directions due lake county fire  cafire wildfires', 'flood disaster heavy rain causes flash flooding streets manitou colorado springs areas', 'im top hill i can see fire woods', 'theres emergency evacuation happening now building across street', 'im afraid tornado coming area', 'three people died heat wave far']
['our deeds reason earthquake may allah forgive us', 'forest fire near la ronge sask canada', 'all residents asked shelter place notified officers no evacuation shelter place orders expected', ' people receive wildfires evacuation orders california', 'just got sent photo ruby alaska smoke wildfires pours school']
label = ['1', '1', '1', '1', '1','1', '1', '1', '1', '1','1']
print("WWWWWWWWWWWWW")
print(len(data))
print(len(label))

#converting the labels to int value
label = list(map(np.int64, label))

#Creating Training Dataset
training_data = tf.data.Dataset.from_tensor_slices((data,label)).prefetch(1)

print(type(training_data))
print(training_data)

# Training
num_epochs = 5
history = model.fit(training_data.shuffle(10000).batch(2), epochs=num_epochs, verbose=2)
