#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 18:06:41 2018
@author: pablorr10

Algoritmo Apriori para el aprendizaje de Reglas de Asociación
"""

import numpy as np
import pandas as pd
from itertools import combinations
from beautifultable import BeautifulTable as btable

datos = pd.read_csv('./problema_tiempo.csv', sep=';')

# Parámetros
COBERTURA_MINIMA = 3
CONFIANZA_MINIMA = 0.6
EJEMPLOS = len(datos)


# Crear Item-Sets
# ===============
class Item_Set:

    def __init__(self, clases, atributos):
        
        self.nombre = str(clases) + ' = ' + str(atributos)
        self.clases = clases
        self.atributos = atributos
        self.cobertura = 0
        self.reglas = []
 
    def calcular_cobertura(self, datos):
        # Functión para calcular la cobertura frente a un conjunto de datos
        self.cobertura = int(np.sum((datos[self.clases].values == self.atributos).all(axis=1)))    
        return self.cobertura

        
# Create all the combinations
clases = []
for i in range(1,5):
#for i in range(1, len(list(datos.columns[1:]))+1):
# Reduce the number of examples to 2 iterations
    combis = list(combinations(datos.columns[1:], i))  
    for j, clase in enumerate(combis):        
        clases.append(list(clase[:i]))

item_sets = []
table = btable(max_width=3000)
table.column_headers = ['Item_Set', 'Cobertura']
for i, cl in enumerate(clases):
    # Para cada combinacion de clases
    idx = list(datos[cl].drop_duplicates().index)
    atributos = datos[cl].loc[idx]
   
    for j in range(len(atributos)):
        
        atributo = list(atributos.iloc[j,:].values)       
        item_set = Item_Set(cl, atributo)
        item_set.calcular_cobertura(datos=datos)
        #item_set.cobertura = cobertura(datos, item_set)
        
        if item_set.cobertura >= COBERTURA_MINIMA:
            table.append_row([item_set.nombre, item_set.cobertura])
            item_sets.append(item_set)
print(table)


    
class Regla:      

    def __init__(self, antecedentes, consecuentes):
        
        nombre = 'SI ' + str(antecedentes[0][0]) + ' = ' + str(antecedentes[0][1])
        for a in range(1, len(antecedentes)):
            nombre += ' Y ' + str(antecedentes[a][0]) + ' = ' + str(antecedentes[a][1]) 
        
        nombre += ' ENTONCES ' + str(consecuentes[0][0]) + ' = ' + str(consecuentes[0][1])
        for c in range(1, len(consecuentes)):
            nombre += ' Y ' + str(consecuentes[c][0]) + ' = ' + str(consecuentes[c][1])
        
        self.nombre = nombre
        self.antecedentes = antecedentes
        self.consecuentes = consecuentes
        self.confianza = 0
        self.soporte = 0
        
    def calcular_confianza(self, datos):
        '''
        Porcentaje de ejemplos que satisfacen el antecedente y consecuente 
        de la regla entre aquellos que solo satisfacen el antecedente
        '''
        numerador = 0
        denominador = 0
    
        antecedentes = self.antecedentes
        consecuentes = self.consecuentes
        
        for antecedente in self.antecedentes:
            
            # Buscamos en los datos filtrando por todos los antecedentes
            if 'si_a' not in locals():
                si_a = datos[datos[antecedente[0]] == antecedente[1]]    
            
            else: si_a = si_a[si_a[antecedente[0]] == antecedente[1]]
            
        denominador = len(si_a)
        
        for consecuente in self.consecuentes:
            
            # Buscamos en los datos filtrando por todos los consecuentes
            # Partimos de los datos que ya tienen filtrados los antecedentes 
            if 'si_c' not in locals():
                si_c = si_a[si_a[consecuente[0]] == consecuente[1]]
                
            else: si_c = si_c[si_c[consecuente[0]] == consecuente[1]]
            
        numerador = len(si_c)
            
        self.confianza = np.round((numerador / denominador), 2)
        self.soporte = np.round((numerador / EJEMPLOS), 2)
        
        
        
    

# Aprender Reglas
# ===============
reglamento = []

table = btable(max_width=3000)
table.column_headers = ['Regla', 'Cobertura']

# Iterar sobre los Item-sets que tengan al menos 2 items
for item_set in item_sets:
    
    # item es 1 solo atributo-valor, k-item_set es k pares atributo-valor
    if len(item_set.atributos) > 1:
    
        reglas = []
        #combinaciones = [list(par) for par in zip(item_set.clases, item_set.atributos)]
        combinaciones = [par for par in zip(item_set.clases, item_set.atributos)]
        
        # Generar todos los posibles antecedentes
        antecedentes = []
        for m in range(1, len(combinaciones)):   
            antecedentes += [list(a[:m]) for a in combinations(combinaciones, m)]
        
        
        # Caso de solo 2 unidades básicas A y B: solo existe la regla A -> B
        if len(antecedentes) < 3:
                
                antecedente = antecedentes[0]
                consecuente = antecedentes[1]
                nueva_regla = Regla(antecedente, consecuente)
                nueva_regla.calcular_confianza(datos)
                
                if nueva_regla.confianza > CONFIANZA_MINIMA:
                    reglas.append(nueva_regla)
                    item_set.reglas = reglas
                
                    table.append_row([nueva_regla.nombre, '%.3f' % nueva_regla.confianza])
                    reglamento.append(nueva_regla)
                
        else:
            
            # Para el resto de caos
            for antecedente in antecedentes:       
                    
                # Posibles consecuentes para el antecedente
                t = len(item_set.atributos)
                r = len(antecedente)
                candidatos = [a for a in antecedentes if len(a) == (t-r) and antecedente not in a]
                
                # Asociar consecuentes
                consecuentes = []
                for _, us in enumerate(candidatos):
                    
                    shouldbreak = False
                    for u in us:
                            
                        if shouldbreak: break
                        for a in antecedente:
                            
                            if (a not in us) and (u not in antecedente):
                                
                                consecuente = us
                                consecuentes.append(consecuente)
                                shouldbreak = True
                                break
                
                for consecuente in consecuentes:
                        
                        nueva_regla = Regla(antecedente, consecuente)
                        nueva_regla.calcular_confianza(datos)
                        
                        if nueva_regla.confianza > CONFIANZA_MINIMA:
                            reglas.append(nueva_regla)
                            item_set.reglas = reglas
                            
                            table.append_row([nueva_regla.nombre, '%.3f' % nueva_regla.confianza])
                            reglamento.append(nueva_regla)
                            
print(table)