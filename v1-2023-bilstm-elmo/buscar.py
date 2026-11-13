#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 21:11:22 2024

@author: mluisadiez
"""

def buscar (nodo,listaanotaciones, listaanotacionespar):
    """print(nodo)"""
    for i in range(0,len(listaanotaciones)):
        if (listaanotaciones[i].attrib["StartNode"]==nodo):
            """print("entri")"""
            listaAtributos=list()
            anotacion=listaanotaciones[i]
            """print("la anotacion")
            print(anotacion)"""
            """ de cada anotación se obtienen sus atributos por separado"""
           
            identif=anotacion.attrib["Id"]
            tipo=anotacion.attrib["Type"]
            start=anotacion.attrib["StartNode"]
            end=anotacion.attrib["EndNode"]
            
            """print("www")
            print(identif)
            print(tipo)
            print(start)
            print (end)
            
            
            print("SSSSSS")"""
            
            s=""
            i=0
            for child in anotacion:         
                """print(child[0].text)
                print(child[1].text)
                print("HHHHHHHHHHHHHHHHHHHHHHHHHH")"""
                """print(child[1].text)"""
                
                if not child[1].text is None:
                    textoc1=" " 
                else:
                    textoc1=child[1].text
                listaAtributos.append(child[0].text)
                """+"="+child[1].text"""
                """print(listaAtributos)"""
                i=i+1
               
            """print("las i")
            print(i)
          
            for i in range(0,len(listaAtributos)):
                s = ''.join(listaAtributos[i])"""
            s='+'.join(listaAtributos)
                
            
                
            if (s):
                return tipo+","+s
            else:
                return tipo
            
    for i in range(0,len(listaanotaciones)):
        if (listaanotaciones[i].attrib["StartNode"]==nodo):
            return "O"
    return "O"