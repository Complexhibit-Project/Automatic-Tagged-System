# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd

df1=pd.read_csv('/Users/mluisadiez/ner_dataset.csv', sep=",",encoding='cp1252')


class SentenceGetter(object):
    def __init__(self,data):
        self.n_sent=1
        self.data=data
        self.empty=False
        agg_func=lambda s:[(w,t) for w,t in zip(s['Word'].values.tolist(), s['Tag'].values.tolist())]
        self.grouped=self.data.groupby("Sentence #").apply(agg_func)
        self.sentences= [s for s in self.grouped]
        
    def get_next(self):
        try:
            s=self.grouped["Sentence: {}".format(self.n_sent)]
            self.n_sent+= 1
            return s
        except:
            return None
        
resultado=SentenceGetter(df1)


"""print(resultado.grouped)"""


"""print(resultado.sentences[3][0][0])
ListaPrueba=list()"""

"""print(resultado.sentences)"""


    



lista=resultado.get_next()

print("la lista")

"""print(resultado.sentences)"""





