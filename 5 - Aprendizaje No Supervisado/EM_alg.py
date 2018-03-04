#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  4 13:03:34 2018

@author: pablorr10
"""

import time
import copy as cp
import numpy as np
import pandas as pd
import random as rand
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from scipy.stats import norm

datos = pd.read_csv('./2d_data_clustering.csv') 
datos.columns = ['x', 'y']

'''Reducing datasat for speeding up coding'''
#datos = datos.iloc[:1300, :]5
columna_cluster = np.random.randint(low=1, high=4, size=len(datos.x))
datos['cluster'] = columna_cluster
datos['cluster'].replace([1,2,3], ['A','B','C'], inplace=True)

datos.head()


# 1 - Valores iniciales
parametros = {'muA': [72, 20],          # μAx, μAy
              'sigA': [[5,0], [0,5]],   # σAx, σAy
              'pA' : [0.3, None],       # pA
              'muB': [10, 36],          # μBx, μBy
              'sigB': [[5,0], [0,5]],   # σBx, σBy
              'pB' : [0.3, None],       # pB
              'muC': [70, 36],          # μCx, μCy
              'sigC': [[15,0], [0,15]], # σCc, σCy
              'pC' : [0.4, None]}       # pC

parametros = pd.DataFrame(parametros)
parametros.head()

plt.figure(figsize=(20,6))
plt.title('Datos iniciales', fontsize=18)
plt.scatter(datos['x'], datos['y'], color='black', s=10)
plt.scatter(parametros.loc[0, 'muA'], parametros.loc[1, 'muA'], 
            marker='P', s=300, c='r')
plt.scatter(parametros.loc[0, 'muB'], parametros.loc[1, 'muB'], 
            marker='P', s=300, c='r')
plt.scatter(parametros.loc[0, 'muC'], parametros.loc[1, 'muC'], 
            marker='P', s=300, c='r')
plt.show()


# Método para calcular la probabilidad
def prob(val, mu, sig, lam):
    '''
    Función que calcular la probabilidad de un punto de pertenecer a un cluster con distribución
    normal dado por los parámetros val, mu, sig, lam
    '''
    p = lam
    for i in range(len(val)):
        p *= norm.pdf(val[i], mu[i], sig[i][i]) # pdf - Función de densidad de probabilidad
        #p *= (np.exp(-0.5 * (np.power((val[i] - mu[i]), 2) / np.power(sig[i][i], 2))) / sig[i][i])
    return p


# Función Esperanza
def esperanza(datos, params):
    '''
    Método que calcula la probabilidad de pertenecer a un cluster y devuelve una ---
    '''
    for i in range(datos.shape[0]):
        # Para cada punto
        x = datos['x'][i]
        y = datos['y'][i]
        p_cluster1 = prob([x,y], 
                          list(params['muA']), 
                          list(params['sigA']), 
                          params['pA'][0])
        p_cluster2 = prob([x,y], 
                          list(params['muB']), 
                          list(params['sigB']), 
                          params['pB'][0])
        p_cluster3 = prob([x,y], 
                          list(params['muC']), 
                          list(params['sigC']), 
                          params['pC'][0])
        
        if p_cluster1 > p_cluster2:
            
            if p_cluster2 > p_cluster3: 
                datos.loc[i, 'cluster'] = 'A'
            
            elif p_cluster1 < p_cluster3:
                datos.loc[i, 'cluster'] = 'C'
                
        elif p_cluster2 > p_cluster3: 
                datos.loc[i, 'cluster'] = 'B'
            
        else: datos.loc[i, 'cluster'] = 'C'
                
    return datos
        
        
# Función maximización
def maximizacion(datos, params):
    '''
    Método que recalcula los valores de los parámetros basando en los resultados de la esperanza
    calculada en el paso anterior de la iteración
    '''
    puntos_cluster_A = datos[datos['cluster'] == 'A'] # Los datos cuya columna cluster sea A
    puntos_cluster_B = datos[datos['cluster'] == 'B']
    puntos_cluster_C = datos[datos['cluster'] == 'C']
    
    porcentaje_en_cluster_A = len(puntos_cluster_A) / float(len(datos))
    porcentaje_en_cluster_B = len(puntos_cluster_B) / float(len(datos))
    porcentaje_en_cluster_C = len(puntos_cluster_C) / float(len(datos))
    
    params['pA'] = porcentaje_en_cluster_A
    params['pB'] = porcentaje_en_cluster_B
    params['pC'] = porcentaje_en_cluster_C
    
    params['muA'] = [np.mean(puntos_cluster_A['x']), np.mean(puntos_cluster_A['y'])]
    params['muB'] = [np.mean(puntos_cluster_B['x']), np.mean(puntos_cluster_B['y'])]
    params['muC'] = [np.mean(puntos_cluster_C['x']), np.mean(puntos_cluster_C['y'])]
    
    params['sigA'] = [[np.std(puntos_cluster_A['x']), 0], [0, np.std(puntos_cluster_A['y'])]]
    params['sigB'] = [[np.std(puntos_cluster_B['x']), 0], [0, np.std(puntos_cluster_B['y'])]]
    params['sigC'] = [[np.std(puntos_cluster_C['x']), 0], [0, np.std(puntos_cluster_C['y'])]]
    
    return params
    
    
    
# Necesitamos una función distancia de nuevo, reformulada un poco, ya que ahora no se mueven 
# las coordenadas de un centroide, sino la media de diferentes distribuciones gaussianas
def distancia(parametros_viejos, parametros_nuevos):
    '''
    Método para calcular la distancia entre puntos y determinar si hemos convergido o seguimos 
    con el proceso de iteración
    '''
    distancia = 0
    for cluster in ['muA', 'muB', 'muC']:
        # Para cada media de cada distribución
        for i in range(len(parametros_viejos)):
            # Para x, y
            distancia += (parametros_viejos.loc[i, cluster] - parametros_nuevos.loc[i, cluster])**2
    
    return np.sqrt(distancia)


def dibujar_elipse(centro, puntos, alpha, color):
    '''
    Método que dibuja la forma elíptica de los clusters dados sus parámetros
    '''
    # Convertir puntos a una lista de arrays de 2 dimensiones
    for i, p in enumerate(puntos):
        puntos[i] = np.array(p)
    
    # Matriz de covarianza
    M_cov = np.cov(puntos, rowvar=False)
    
    # Autovalores y autovectores de la matriz de covarianza
    autovalores, autovector = np.linalg.eigh(M_cov)
    rango_matrix = autovalores.argsort()[::-1]
    autovector = autovector[:, rango_matrix]
    
    # Calcular el ángulo de la elipse dado los autovectores
    angulo = np.degrees(np.arctan2(*autovector[:,0][::-1]))
    
    # Calcular la altura y la anchura dados los autovalores
    ancho, alto = 4  * np.sqrt(autovalores[rango_matrix])
    
    # Construimos el objeto elipse
    elipse = Ellipse(xy=centro, width=ancho, height=alto, angle=angulo, 
                    alpha=alpha, color=color)
    
    ax = plt.gca()
    ax.add_artist(elipse)
    
    return elipse
    
    
# Cuerpo del algoritmo EM - Iteraciones

# Parámetros del algoritmo EM
cambio = np.float('inf') # Le asignamos un valor inicial enorme (infinito)
umbral = 0.01 # El valor el cual estamos dispuestos a tolerar como distancia aceptable
iteraciones = 0
copia_datos = cp.deepcopy(datos)
last_it = 0


# Bucle para iterar
start = time.time()
while (cambio > umbral) and (iteraciones <10):
    # Mientras que el cambio sea mayor que el límite que toleramos
    iteraciones += 1
    
    # Esperanza
    cluster_actualizados = esperanza(datos.copy(), parametros)
    
    # Maximización
    parametros_actualizados = maximizacion(cluster_actualizados, parametros.copy())
    
    # Calcular el cambio de las estimaciones
    cambio = distancia(parametros, parametros_actualizados)
    
    # Imprimir para seguir por donde va el algoritmo
    finish = time.time()
    print('Interación número: %d, cambio = %d' % (iteraciones, cambio))
    #print('Tiempo de iteración: %.2f segundos' & ((finish - last_it)))
    print('Tiempo de ejecución: %.2f segundos' % ((finish-start)))
    last_it = time.time()
    
    # Actualizar los clusters y los parametros para la siguiente iteracion
    datos = cluster_actualizados
    parametros = parametros_actualizados
    
    # Imprimir algunas de las iteraciones para ver el progreso
    if iteraciones % 1 == 0: # Aquí podremos controlar cada cuantas hacemos una figura
        
        datos_pintar = cp.deepcopy(datos)
        datos_pintar['cluster'].replace([1,2,3], ['A','B','C'], inplace=True)
        
        colors = {'A': 'blue', 'B': 'green', 'C': 'brown'}
        
        plt.figure() 
        plt.scatter(datos['x'], datos['y'], 10, 
                    c=datos['cluster'].apply(lambda x: colors[x]))
        plt.scatter(parametros_actualizados.loc[0, 'muA'], 
                    parametros_actualizados.loc[1, 'muA'], marker='P', s=300, c='k')
        plt.scatter(parametros_actualizados.loc[0, 'muB'], 
                    parametros_actualizados.loc[1, 'muB'], marker='P', s=300, c='k')
        plt.scatter(parametros_actualizados.loc[0, 'muC'], 
                    parametros_actualizados.loc[1, 'muC'], marker='P', s=300, c='k')
        
'''        
# Pintar Elipses
puntos_cluster_A = datos[datos['cluster'] == 'A'] 
puntos_A = list(zip(puntos_cluster_A['x'], puntos_cluster_A['y']))

puntos_cluster_B = datos[datos['cluster'] == 'B']
puntos_B = list(zip(puntos_cluster_B['x'], puntos_cluster_B['y']))

puntos_cluster_C = datos[datos['cluster'] == 'C']
puntos_C = list(zip(puntos_cluster_C['x'], puntos_cluster_C['y']))

colores = ['red', 'blue', 'green']

dibujar_elipse(centro=(parametros_actualizados.loc[0, 'muA'],
                       parametros_actualizados.loc[1, 'muA']),
               puntos=puntos_A, 
               alpha=0.2, color=colores[0])

dibujar_elipse(centro=(parametros_actualizados.loc[0, 'muB'],
                       parametros_actualizados.loc[1, 'muB']),
               puntos=puntos_B, 
               alpha=0.2, color=colores[1])

dibujar_elipse(centro=(parametros_actualizados.loc[0, 'muC'],
                       parametros_actualizados.loc[1, 'muC']),
               puntos=puntos_C, 
               alpha=0.2, color=colores[2])

plt.show()
'''