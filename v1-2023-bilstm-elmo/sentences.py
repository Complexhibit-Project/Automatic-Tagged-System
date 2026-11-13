#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 28 20:38:08 2023

@author: mluisadiez
"""

     
class Sentences_Getter(object):
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
