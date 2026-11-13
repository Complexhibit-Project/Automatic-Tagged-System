#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 20:40:23 2024

@author: mluisadiez
"""

import xml.etree.ElementTree as ET
import os

import pandas as pd
import numpy as np
import pickle
import nltk
import buscar
import contruirlistas
import prepararDatos
import preparacionDatos
"""nltk.download()"""
from nltk.tokenize import word_tokenize, sent_tokenize
import matplotlib.pyplot as plt

listaTextos=list()
listaNodos=list() 
listaTipos=list()
listaAtributos=list()
ejemplo_dir = '/Users/mluisadiez/100_COMPLETOS/XML_GATE/'

with os.scandir(ejemplo_dir) as ficheros:
    
    for fichero in ficheros: 
        print(fichero.name)
        tree = ET.parse(ejemplo_dir+"catalogo-exposicic393n-de-arte.xml")

        root = tree.getroot()
        
        
        
        anotaciones=root[2] 
        
        listaAnotaciones=list()
        
        listaAnotaciones.append(anotaciones)
        verAnotacion=listaAnotaciones[0]
        
        if (len(root)==4): 
            anotacionespar=root[3]
        else:
            anotacionespar=""
        
        listaAnotacionespar=list()
        
        listaAnotacionespar.append(anotacionespar)
        verAnotacionpar=listaAnotacionespar[0]
        
        
        
        
        
        for i in range(0,len(root[1])):
           
            if ('.' in root[1][i].tail):
                
                listaTextos.append(root[1][i].tail[:-1])
                listaNodos.append(root[1][i].attrib["id"])
                tipoencontrado=buscar.buscar(root[1][i].attrib["id"],verAnotacion,verAnotacionpar)
                
                
                if ("," in tipoencontrado):
                    tipo_final=tipoencontrado.split(",")
                    listaTipos.append(tipo_final[0])
                    listaAtributos.append(tipo_final[1])
                else:
                    
                    listaTipos.append(tipoencontrado)
                    listaAtributos.append([])
                listaTextos.append(".")
                listaNodos.append("")
                listaTipos.append("O")
                listaAtributos.append([])
            else: 
                
                listaTextos.append(root[1][i].tail)
                listaNodos.append(root[1][i].attrib["id"])
                tipoencontrado=buscar.buscar(root[1][i].attrib["id"],verAnotacion,verAnotacionpar)
                
                
                if ("," in tipoencontrado):
                    tipo_final=tipoencontrado.split(",")
                    listaTipos.append(tipo_final[0])
                    listaAtributos.append(tipo_final[1])
                else:
                    
                    listaTipos.append(tipoencontrado)
                    listaAtributos.append([])
            
  
datos={'texto':listaTextos,'nodo':listaNodos,'tipo':listaTipos,'atributos':listaAtributos}

df=pd.DataFrame(data=datos)





tabla_resultante=contruirlistas.buscar_frases(df)



"""archivo="/Users/mluisadiez/ner_dataset_new.xlsx"
tabla_resultante=pd.read_excel(archivo)"""

 
tabla_resultante=contruirlistas.buscar_frases(df) 
print("la tabla")
print(tabla_resultante)    
tabla_resultante.to_excel("data_exporttabla.xlsx", sheet_name="Sheet1")
preparacionDatos.preparar_datos(tabla_resultante)
    









    