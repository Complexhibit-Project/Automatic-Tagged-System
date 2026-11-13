#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 20:40:23 2024

@author: mluisadiez
"""

import xml.etree.ElementTree as ET



import buscar

"""nltk.download()"""

def procesar_texto(archivo):
    print("hola")    
    tree = ET.parse(archivo)
    
    root = tree.getroot()
    
    
    print(len(root))
    anotaciones=root[2]
    
    listaAnotaciones=list()
    
    listaAnotaciones.append(anotaciones)
    verAnotacion=listaAnotaciones[0]
    
    if (len(root)==4): 
        anotacionespar=root[3]
    else:
        anotacionespar=[]
    
    listaAnotacionespar=list()
    
    listaAnotacionespar.append(anotacionespar)
    verAnotacionpar=listaAnotacionespar[0]
    
    
    listaTextos=list()
    listaNodos=list()
    listaTipos=list()
    listaAtributos=list()
    
    
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
        
      
   
    
    
    
    """archivo="/Users/mluisadiez/ner_dataset_new.xlsx"
    tabla_resultante=pd.read_excel(archivo)"""
    
    return [listaTextos,listaNodos,listaTipos,listaAtributos]







    

    