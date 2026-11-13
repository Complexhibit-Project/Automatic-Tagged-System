#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 09:58:09 2024

@author: mluisadiez
"""

import pandas as pd
import numpy as np
import os

def buscar_frases(dforiginal):
   lista_num_sentencia=list()
   lista_frases=list()
   lista_frase=list()
   lista_etiquetas=list()
   lista_etiquetas_frase=list()
   nums=1
   datos=dforiginal.to_numpy().transpose().tolist()
   
   for i in range(0, len(datos[0])):
       print("ESTE EEEE")
       print(datos[0][i])
       texto = datos[0][i].split()
       """print(texto)"""
       if (datos[2][i]!="O"):
           for j in range(0,len(texto)):
               cadenaatributos=""
               if (len(datos[3][i])!=0):
                   cadenaatributos=","
                   for k in range(0,len(datos[3][i])):
                       cadenaatributos+=datos[3][i][k]
               
               if (j==0):
                   lista_frase.append(texto[j])
                   """print("longitud atrib")
                   print(datos)"""
                   """lista_etiquetas.append(datos[2][i]+"-B"+cadenaatributos)"""
                   lista_etiquetas.append(datos[2][i]+"-B")
               elif (j<len(texto)-1):
                   lista_frase.append(texto[j])
                   """lista_etiquetas.append(datos[2][i]+cadenaatributos)"""
                   lista_etiquetas.append(datos[2][i]+"-I")
               else:
                   lista_frase.append(texto[j])
                   """lista_etiquetas.append(datos[2][i]+"-E"+cadenaatributos)"""
                   lista_etiquetas.append(datos[2][i]+"-E")
           print("lista frasesssssssssssssssssssss")
           """print(lista_frase)"""
           print("lista etiquetasssssss")
           """print(lista_etiquetas)"""
    
       elif (len(texto)!=0):
           """print("NO ENTRA POR AQUI POR TODO ")
           print(texto)"""
           for j in range(0,len(texto)):
               lista_frase.append(texto[j])
               lista_etiquetas.append("O")
       else:
           """print(texto)"""
           lista_num_sentencia.append("Sentence: "+str(nums))
           lista_frases.append(lista_frase)
           lista_etiquetas_frase.append(lista_etiquetas)
           lista_etiquetas=list()
           lista_frase=list()
           nums+=1
           
               
    
   """print("LISTA FRASES PARA DATA FRAME")
   print(lista_frases)
   print("LISTA ETIUQTEASPARA DATA FRAME")
   print(lista_etiquetas_frase)
   print(lista_num_sentencia)"""
   
   datos={'Sentence #':lista_num_sentencia,'Word':lista_frases,'Tag':lista_etiquetas_frase}
   
   df=pd.DataFrame(data=datos)

   
   
   words=set()
   
   for i in range(0,len(lista_frases)):
       for j in range(0,len(lista_frases[i])):
           words.add(lista_frases[i][j])
           
   words2index = {w:i for i,w in enumerate (words) }
   """print(words2index)"""
     
   datosdf=df.to_numpy().transpose().tolist()
   """print(datosdf[2])"""       
       
   tags=set()
   
   for i in range(0,len(lista_etiquetas_frase)):
       for j in range(0,len(lista_etiquetas_frase[i])):
           tags.add(lista_etiquetas_frase[i][j])
   
   tags2index = {w:i for i,w in enumerate (tags) }
   print("tag 2 index")
   print(tags2index)
   
   
   
   
   lista_indice_data=list()
   lista_indices=list()
   for i in range(0,len(datosdf[1])):
       for j in range(0,len(datosdf[1][i])):
           palabra=datosdf[1][i][j]
           print(palabra)
           lista_indices.append(int(words2index[palabra]))
       lista_indice_data.append(lista_indices)
       lista_indices=list()
       
   lista_indice_tag=list()
   lista_indicestag=list()
   for i in range(0,len(datosdf[2])):
        for j in range(0,len(datosdf[2][i])):
            tag=datosdf[2][i][j]
            lista_indicestag.append(int(tags2index[tag]))
        lista_indice_tag.append(lista_indicestag)
        lista_indicestag=list()
     
   print(lista_indice_data)
   print(lista_indice_tag)
   datos={'Sentence #':lista_num_sentencia,'Word':lista_frases,'Tag':lista_etiquetas_frase,"Word_idx":lista_indice_data,"Tag_idx":lista_indice_tag}
   
   df=pd.DataFrame(data=datos)
   
   print(df)
   
   print(df.loc[df['Sentence #']=='Sentence: 14'])
   
   df.to_excel("data_export.xlsx", sheet_name="Sheet1")
    
   return df
    