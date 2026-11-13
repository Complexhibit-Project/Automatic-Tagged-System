#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 28 21:49:34 2023

@author: mluisadiez
"""

import xml.etree.ElementTree as ET
import os

import pandas as pd
import numpy as np
import pickle
import nltk
"""nltk.download()"""
from nltk.tokenize import word_tokenize, sent_tokenize
import procesartexto
import preparacionDatos
import contruirlistas
import matplotlib.pyplot as plt
import torch
pd.options.display.max_columns = None

mps_device = torch.device("mps")

with open('/Users/mluisadiez/catalogo-exposicic393n-de-arte.xml', 'r') as f:
  xml_text = f.read().splitlines()
  xml_text = ''.join(xml_text).encode('utf-8')
  


listaTotalsentencias=list()
tablaAnotaciones=pd.DataFrame() 
tablaAnotaciones["Id"]=None
tablaAnotaciones["Type"]=None
tablaAnotaciones["StartNode"]=None
tablaAnotaciones["EndNode"]=None
tablaAnotaciones["Atributos"]=list()
listaanotaciones=list()

ejemplo_dir = '/Users/mluisadiez/100_COMPLETOS/XML_GATE/'

listaTextos=[]
listaNodos=[]
listaTipos=[]
listaAtributos=[]
with os.scandir(ejemplo_dir) as ficheros:
    
    for fichero in ficheros:
        
        print(fichero.name)
        tabla_res=procesartexto.procesar_texto(ejemplo_dir+fichero.name)
        print("AAAAAAAAAAAAAAAAAAAAAA")
        
        listaTextos.append(tabla_res[0])
        print(listaTextos)
        listaNodos.append(tabla_res[1])
        listaTipos.append(tabla_res[2])
        listaAtributos.append(tabla_res[3])
        break;
        
    datos={'texto':listaTextos,'nodo':listaNodos,'tipo':listaTipos,'atributos':listaAtributos}
     
    df=pd.DataFrame(data=datos)
     
    print(df)
     
     
     
    tabla_resultante=contruirlistas.buscar_frases(df) 
    print("la tabla")
    print(tabla_resultante)    
    tabla_resultante.to_excel("data_exporttabla.xlsx", sheet_name="Sheet1")
    preparacionDatos.preparar_datos(tabla_resultante)
        
    print("hola")


