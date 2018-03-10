#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 17:35:49 2017

@author: pablorr10
"""

class nodo:

    @staticmethod 
    # Los métodos estáticos no pasan la clase ni la instancia, pero conviene meterlos dentro de la clase porque tiene relación con sus atributos
    def calcular_coste(estado, objetivo, function):

        '''
        Función que calcula el coste del estado actual en función de:
            
        :Estado: Lista representando los 8 posibles estados del puzzle
        :Objetivo: Lista representado el estado objetivo al que se quiere llegar
        :Function: 2 posibilidades: f1 = sitio_incorrecto, f2 = distancia Manhattan
        '''
        # Coste heurístico inicial
        h_coste = 0 
        
        # h1 = Número de piezas que no están en el sitio que les corresponde
        if function == 'sitio_incorrecto':
            for x in zip(estado, objetivo):
                if x[0] != x[1]:
                    h_coste += 1 # If we haven't improve, increase the cost of making a movimiento
                else:
                    continue

        # h2 = Manhattan Distance
        elif function == 'distancia_manhattan':
            for x in objetivo:
                h_coste += abs(objetivo.index(x) - estado.index(x))

        return h_coste


    def __init__(self, key, estado, parent, g_n, profundidad, h_funcion, objetivo, movimiento):

        '''
        Clase para crear los ramas del árbol, cada vez que se la llame se creará una instancia rama
        :Key: índice para identificar al rama
        :Estado: estado del rama
        :Padre: la 'key' del rama padre
        :g_n: g(n) es el coste de movimientor, variable acumulativa
        :Profundidad: la profundidad del rama en el árbol
        :h_funcion: función heurística para calcular el coste h
        :Objetivo: lista representado el estado objetivo al que se quiere llegar
        :Movimiento: movimiento realizado para llegar a este estado
        :Coste_total
        :Movimientos: lista de los movimientos disponibles
        **buscar_movimientos: función que devuelve los posibles movimientos que podemos hacer
        '''

        self.key = key
        self.estado = estado
        self.parent = parent
        self.g_n = g_n
        self.profundidad = profundidad
        self.h_funcion = h_funcion
        self.objetivo = objetivo
        self.movimiento = movimiento
        self.h_n = nodo.calcular_coste(self.estado , self.objetivo , self.h_funcion)
        self.coste_total = self.g_n + self.h_n
        self.buscar_movimientos()

    def buscar_movimientos(self):

        '''
        Función que devuelve los posibles movimientos que podemos hacer
        '''
        
        self.movimientos = []

        # Los movimientos disponibles se tienen que programar a mano, en función de la posición en donde esté el hueco
        if    self.estado.index(0) == 0:  self.movimientos.extend(('izquierda','arriba'))
        elif  self.estado.index(0) == 1:  self.movimientos.extend(('izquierda','derecha','arriba'))
        elif  self.estado.index(0) == 2:  self.movimientos.extend(('derecha','arriba'))
        elif  self.estado.index(0) == 3:  self.movimientos.extend(('arriba','abajo', 'izquierda'))
        elif  self.estado.index(0) == 4:  self.movimientos.extend(('arriba','abajo','izquierda','derecha',))
        elif  self.estado.index(0) == 5:  self.movimientos.extend(('derecha','arriba', 'abajo'))
        elif  self.estado.index(0) == 6:  self.movimientos.extend(('abajo','izquierda'))
        elif  self.estado.index(0) == 7:  self.movimientos.extend(('izquierda','derecha', 'abajo'))
        else: self.movimientos.extend(('derecha','abajo'))
    
    def mover_pieza(self, movimiento):

        '''
        Método para mover la pieza, es decir, actualizar nuestro estado.
        Para ello, en función del moviento que se pase, actualizará el índice donde está el 0 y donde estaba el 0 se pondrá el valor que se pasa a ocupar
        '''

        nuevo_rama = self.estado[:]
        cero_idx = nuevo_rama.index(0)

        if    movimiento == 'izquierda': rep_idx = cero_idx + 1
        elif  movimiento == 'derecha':   rep_idx = cero_idx - 1
        elif  movimiento == 'arriba':    rep_idx = cero_idx + 3
        else: rep_idx = cero_idx - 3

        rep_val = self.estado[rep_idx]
        nuevo_rama[cero_idx] = rep_val
        nuevo_rama[rep_idx] = 0
        return nuevo_rama , rep_val

class rama:

    def __init__(self, algoritmo, estado_objetivo):

        '''
        Clase para generar una rama en la creación del árbol. La rama almacenará en una lista los elementos de la clase rama
        :Algoritmo: de momento introduciremos el algoritmo 'a*'
        '''
        self.algoritmo = algoritmo
        self.rama = []

    def elegir_rama(self):

        '''
        Función para devolver el rama nuevo (objeto de clase rama)
        '''
        # Aquí podemos introducir diferentes algoritmos de búsuqeda que mejoren lo que tenemos! Por ahora, siempre se cumplirá el if
        if self.algoritmo == 'a_star': 
            return sorted(self.rama, key=lambda x: x.coste_total)[0] # Devuelve el rama con el mínimo coste

class ArbolDeBusqueda:

    def __init__(self, rama_inicial, estado_objetivo, algoritmo, iterar_profundo):

        '''
        a class to iteratively create a search arbol and solve the 8 puzzle
        :rama_inicial: onjeto de clase rama para comenzar
        :Estado_objetivo: Lista representando el estado al que queremos llegar
        :Algoritmo: algoritmo de búsqueda elegido (de momento solo a*)
        :Funcion_heuristica: función heurísitica para calcular el coste, heredado del rama
        :key: ley usada para iterar sobre los ramas
        :Contador_de_movimientos: se aumenta cuando se excluye un rama que no ha sido visitado
        :Arbol: diccionario de Python para almacenar los ramas de nuestro arbol
        :rama: objeto de clase rama que almacena los ramas que devolverá cuando la llamen
        :estados_visitados: lista de los estados visitados
        :nivel_de_profundidad:lista para almacenar el nivel de profundidad en la búsqueda
        :limite: used for iterative deepening, the profundidad limite the search arbol can currently go to
        '''

        self.estado_objetivo = rama_inicial.objetivo
        self.rama_actual = rama_inicial
        self.root = rama_inicial
        self.algoritmo = algoritmo
        self.funcion_heuristica = rama_inicial.h_funcion
        self.iterar_profundo = iterar_profundo
        self.key = 0
        self.contador_de_movimientos = 0
        self.arbol = {}
        self.rama = rama(self.algoritmo, self.estado_objetivo)
        self.rama.rama.append(self.root)
        self.estados_visitados = []
        self.nivel_de_profundidad = 0
        self.limite = 0
        self.arbol[0] = self.root
        self.resolver()

    def resolver(self):

        '''
        Función para usar iterativamente mientras nos movamos por los ramas del árbol
        '''

        import time
        inicio = time.time()
        self.rama_actual = self.rama.elegir_rama()

        while self.rama:

            # Creamos la variabe longitud_rama para al final poder preguntar la longitud que tiene fácilmente
            longitud_rama = []
            longitud_rama.append(len(self.rama.rama))

            # Comprobar que estamos convergiendo al objetivo (sino hemos mejorado no seguiremos por esta rama a más profunidad)
            if self.rama_actual.estado != self.estado_objetivo:

                # Si hemos decidido seguir a más profundidad en este rama reseteamos el arbol y aumentamos el contador de profundidad
                if self.iterar_profundo:
                    if self.nivel_de_profundidad > self.limite:
                        self.limite += 1
                        self.key = 0
                        self.contador_de_movimientos = 0
                        self.arbol = {}
                        self.rama = rama(self.algoritmo, self.estado_objetivo)
                        self.rama.rama.append(self.root)
                        self.estados_visitados = []
                        self.nivel_de_profundidad = 0
                        self.rama_actual = self.root
                    else:  pass
                else:  pass

                # Comprobamos que no hemos tomado una acción que nos devuelva al estado previo (este es el segundo criterio para abandonar esta rama)
                if self.rama_actual.estado not in self.estados_visitados:
                    self.estados_visitados.append(self.rama_actual.estado[:])
                    self.contador_de_movimientos+=1

                    # Para el rama donde estamos, que pruebe en todos sus posibles futuros, y nos devuelva el coste de elegir cada uno de ellos
                    for movimiento in self.rama_actual.movimientos:
                        self.key += 1
                        new_estado , g_n = self.rama_actual.mover_pieza(movimiento)
                        g_n += self.rama_actual.g_n
                        nuevo_rama = nodo(key=self.key,estado=new_estado,parent=self.rama_actual.key,g_n = g_n,profundidad=self.nivel_de_profundidad+1,\
                                        h_funcion=self.funcion_heuristica,objetivo=self.estado_objetivo,movimiento=movimiento)
                        self.arbol[self.key] = nuevo_rama
                        
                        # Vamos a la rama y vemos si existe el estado con menor coste. De ser así, vemos si el estado de este estado mejor lo que tenemos
                        # Si no, lo dejamos en la rama porque nuestra rama terminara aquí.
                        if self.algoritmo == 'a_star': # aqui pondremos is in [lista de posibles algoritmos] cuando pongamos más!
                            c = 0
                            if self.algoritmo == 'a_star':  sort = 'coste_total'
                            else:  pass

                            for i in self.rama.rama:
                                    if i.estado == nuevo_rama.estado:
                                        if getattr(i,sort) > getattr(nuevo_rama,sort):
                                            del self.rama.rama[c]
                                        else:  c+=1
                                    else:  c += 1

                        else:  pass

                        self.rama.rama.append(nuevo_rama)

                    # Añadimos 1 nivel de profundidad y devolvemos el rama al principio del bucle while
                    self.nivel_de_profundidad+=1
                    self.rama_actual = self.rama.elegir_rama()

                else:
                    # Esta funcionalidad cambiará para otros algoritmos de búsqueda, por eso lo dejamos así de momento
                    if self.algoritmo != 'a_star':  idx = -1
                    else:  idx = 0

                    if self.algoritmo == 'a_star':  self.rama.rama = sorted(self.rama.rama, key=lambda x: x.coste_total)
                    else:  pass

                    # Borramos un objeto de la ramma basado en el index
                    del self.rama.rama[idx]
                    self.rama_actual = self.rama.elegir_rama()

            else:
                # El puzzle ya está resuelto, salir del bucle
                break

        # Pintamos ahora los resultados, Iteramos sobre el árbol hacia atrás hasta encontrar el camino que lleva al rama inicial
        final = time.time()
        for k,v in self.arbol.items():
            if v.estado == self.estado_objetivo:
                kinit = k
                break
            else:  continue
        
        # Añadimos los valores al revés para pintar bien el resultado
        path_list = [kinit]
        while kinit != 0:
            path_list.insert(0, self.arbol[kinit].parent)
            kinit = path_list[0]

        # Añadimos una descripción técnica de la resolución y los pasos que hemos ido tomando
        for i in path_list:
            print ('Movimiento:', self.arbol[i].movimiento, '\n', 'Coste heurístico', self.arbol[i].h_n, '\n', 'Total Cost:',self.arbol[i].g_n)
            # Printamos el resultado de la iteración para ver como ha ido evolucionand  
            table = BT(max_width=3000)
            #table.column_headers = ['Variable', 'Sigmoid', 'SGD']
            table.append_row(self.arbol[i].estado[0:3])
            table.append_row(self.arbol[i].estado[3:6])
            table.append_row(self.arbol[ i].estado[6:])
            print(table)

        print('\n')
        print('Total movimientos: ', len(path_list) - 1) # don't include the initial estado as a movimiento
        print('8 Puzzle Resuelto', '\n', '~~Max logitud de rama:', max(longitud_rama), '\n', '~~ramas creados:', self.contador_de_movimientos, '\n',\
            '~~Tiempo de ejecución:', final - inicio, '\n', '~~Total movimientos:', self.contador_de_movimientos, '\n')

from beautifultable import BeautifulTable as BT
objetivo = [1,2,3,8,0,4,7,6,5]
inicio = [2,8,3,1,6,4,7,0,5]
#tester = [1,0,3,8,2,4,7,6,5]
hfun = 'fuera_de_posicion'
algoritmo = 'a_star' # Aquí eligiríamos el algoritmo a usar, de momento solo hemos creado a_star
ideep = False
nodo_inicial = nodo(key=0, estado=inicio, parent=0, g_n=0, profundidad=0,
                 h_funcion=hfun, objetivo=objetivo, movimiento='Initial estado')

test = ArbolDeBusqueda(nodo_inicial, estado_objetivo=objetivo, algoritmo=algoritmo, iterar_profundo=ideep)
