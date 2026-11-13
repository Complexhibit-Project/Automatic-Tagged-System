#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 21:16:45 2024

@author: mluisadiez
"""


    
   
   
    """ elmo_model_path = "https://tfhub.dev/google/elmo/3"
    elmo_layer = hub.KerasLayer(elmo_model_path, input_shape=[], dtype=tf.string, trainable=False)

    model = tf.keras.Sequential([
        elmo_layer,
        tf.keras.layers.Dense(8, activation='sigmoid'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])"""
    
    
    elmo = hub.load("https://tfhub.dev/google/elmo/2").signatures["default"]
    input_text = Input (shape= (max_len,), dtype=tf.string)
    embeddings = elmo(tf.constant(X_tr))["elmo"]
    
    x = Bidirectional(LSTM(units=512, return_sequences=True,recurrent_dropout=0.2, dropout=0.2))(embeddings)
    x_rnn = Bidirectional(LSTM(units=512, return_sequences=True,
                           recurrent_dropout=0.2, dropout=0.2))(x)
    """conexion residual al primer biLSTM"""
    x = add([x, x_rnn]) 
    out = TimeDistributed(Dense(n_tags, activation="softmax"))(x)
    
    model = Model(input_text, out)
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    
    history = model.fit(np.array(X_tr), y_tr, validation_data=(np.array(X_val), y_val),
                    batch_size=batch_size, epochs=5, verbose=1)
    
    hist = pd.DataFrame(history.history)
    plt.figure(figsize=(12,12))
    plt.plot(hist["acc"])
    plt.plot(hist["val_acc"])
    plt.title("Learning curves")
    plt.legend()
plt.show()
    """# Setting hyperparameter  
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)
    model.compile(loss='binary_crossentropy',optimizer=optimizer,metrics=['accuracy'])
    print("www")
    # Model Summary
    model.summary()
    print("WWW")"""
    """training_data = tf.data.Dataset.from_tensor_slices((X_tr,y_tr)).prefetch(1)"""
    
    
    """data = ['our deeds reason earthquake may allah forgive us', 'forest fire near la ronge sask canada', 'all residents asked shelter place notified officers no evacuation shelter place orders expected', ' people receive wildfires evacuation orders california', 'just got sent photo ruby alaska smoke wildfires pours school', 'rockyfire update  california hwy  closed directions due lake county fire  cafire wildfires', 'flood disaster heavy rain causes flash flooding streets manitou colorado springs areas', 'im top hill i can see fire woods', 'theres emergency evacuation happening now building across street', 'im afraid tornado coming area', 'three people died heat wave far']
    ['our deeds reason earthquake may allah forgive us', 'forest fire near la ronge sask canada', 'all residents asked shelter place notified officers no evacuation shelter place orders expected', ' people receive wildfires evacuation orders california', 'just got sent photo ruby alaska smoke wildfires pours school']
    label = ['1', '1', '1', '1', '1','1', '1', '1', '1', '1','1']
    
   
    for i in range(0,len(X_tr)):
        training_data = tf.data.Dataset.from_tensor_slices((X_tr[i],y_tr[i])).prefetch(1)
    
    num_epochs = 5
    history = model.fit(training_data.shuffle(10000).batch(2), epochs=num_epochs, verbose=2)
    print(history)"""
    
