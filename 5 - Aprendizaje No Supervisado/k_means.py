#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 19:37:33 2018

@author: pablorr10
"""

import copy as cp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Importar los datos
datos = pd.read_csv('./2d_data_clustering.csv')
print('Forma de los datos: ', datos.shape)
datos.head(3)

# Separar las variables y representar los datos iniciales
x1 = datos['V1'].values
x2 = datos['V2'].values

X = np.array(list(zip(x1, x2))) # ** Método zip de Python **

plt.figure(figsize=(20,6))
plt.title('Datos iniciales', fontsize=18)
plt.scatter(x1, x2, color='black', s=10)
plt.show()

# Función para calcular la distancia euclídea
def distancia(a, b, ax=1):
    # El método norm del módulo de algebra dentro de numpy nos devuelve la norma de la ecuación
    # que introduzcamos dentro. En nuestro caso, la distancia entre dos puntos es su resta.
    return np.linalg.norm(a - b, axis=ax) 


# Parámetros iniciales

# Número de clusters
k = 3

# Coordenadas de los Centroides 
# Queremos k valores (3) aleatorios entre 0 y el máximo menos un margen (sabemos que un centroide
# no puede estar en una esquina, porque no sería un CENTROide)
c_x = np.random.randint(0, np.max(X)-20, size=k) 
c_y = np.random.randint(0, np.max(X)-20, size=k)

# Almacenar los valores de los centroides en una sola variable C
C = np.array(list(zip(c_x, c_y)), dtype=np.float32)
print(C)

# Visualizar dónde están los centroides
plt.figure(figsize=(20,6))
plt.title('Datos iniciales', fontsize=18)
plt.scatter(x1, x2, color='black', s=10)
plt.scatter(c_x, c_y, marker='P', s=300, c='r')
plt.show()


# Crear la variable C_o para guardar los valores de los centroides antes de actualizarlos.
C_o = np.zeros(C.shape) # Primero inicializamos un vector del tamaño de C con todo ceros

# Creamos la variable clusters de la misma longitud que X, que guardará el cluster al que 
# pertenece cada punto. Por ejemplo, el valor quinto de clusters guarda el cluster al que
# pertenece el quinto punto guardado en X
clusters = np.zeros(len(X))

# Creamos la variable error que mide la distancia entre los nuevos centroides y los antiguos
error = distancia(C, C_o, None)

# PASO 4 - Creamos un bucle que se repita hasta que el error sea 0
while error != 0:
    # PASO 2 - Asignamos los puntos a sus clusters en función de su distancia
    for i in range(len(X)):
        # Calculamos la distancia a los centroides para cada punto
        distancias = distancia(X[i], C)
        # Buscamos cual es la distancia mínima - ** argmin devuelve el índice dónde se encuentra
        cluster = np.argmin(distancias) 
        clusters[i] = cluster

    # Guardamos el valor de los centroides antiguos (utilizamos la función copy de Python)
    C_o = cp.deepcopy(C)
    
    # PASO 3 - Calculamos los nuevos centroides
    for i in range(k):
        # Para cada centroide k
        puntos = [X[j] for j in range(len(X)) if clusters[j] == i] # **List Comprehesion**
        C[i] = np.mean(puntos, axis=0).reshape(2,)
        
    error = distancia(C, C_o, None)

colores = ['y', 'g', 'b']
fig = plt.figure(figsize=(20,6))
for i in range(k):
    # Para cada cluster
    puntos = np.array([X[j] for j in range(len(X)) if clusters[j] == i])
    plt.scatter(puntos[:, 0], puntos[:, 1], s=10, color=colores[i])
plt.scatter(C[:,0], C[:,1], marker='P', s=300, c='r')
plt.show()