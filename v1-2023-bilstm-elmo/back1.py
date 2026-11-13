#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 05:48:39 2023

@author: mluisadiez
"""

diccionarioAnotaciones=anotaciones[0].attrib
np.save('file.npy', diccionarioAnotaciones)
new_dict = np.load('file.npy', allow_pickle='TRUE')
print("wwwwww")
print(new_dict)



for anotacion in anotaciones:
    
    diccionarioNuevo={}
    print(diccionarioNuevo)
    diccionarioNuevo=anotacion.attrib
    if (len(anotacion)>0):
       listaatributos=list()
       for i in range(len(anotacion)):
           listaatributos.append((anotacion[i][0].text,anotacion[i][1].text))
       diccionarioNuevo['Atributos']=listaatributos
    else:
       diccionarioNuevo['Atributos']=list()
       
    listaanotaciones.append(diccionarioNuevo)
    
    
    anotaciones2=None
    anotaciones=root[2]
    if len(root)>3: 
        anotaciones2=root[3]
        fila={"Id":anotacion['Id'], "Type":anotacion['Type'], }
        
        
    with open("obj.pickle", "wb") as f:
          pickle.dump(root[1], f)
          
    with open("obj.pickle", "rb") as f:
          obj = pickle.load(f)
          # Imprime [1, 2, 3, 4].
          print(obj[0])