import random
import numpy as np
import pandas as pd
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx

with open('data\dpc-covid19-ita-province.json') as f:
    d = json.load(f)




def data_cleaning(ls):
    
    '''Funzione che ritorna una dizionario di dati puliti, nel caso in cui venga
    passata una lista di dizionari.
    Il dizionario ritornato ha come chiavi le sigle delle province, e come
    valori le tuple (latitudine, longitudine).'''

    cleaned = {} # creo anche un dizionario con il duplice scopo di accelerare i tempi di controllo quando faccio il while se una provincia è già stata memorizzata e per memorizzare le posizioni
    i = 0
    while i < len(ls) and ls[i].get('sigla_provincia') not in cleaned: # faccio un while in modo che si fermi al primo doppione
        if ls[i].get('sigla_provincia') != '':
            cleaned[ls[i].get('sigla_provincia')] = (ls[i].get('lat'), ls[i].get('long'))
        i += 1
    return cleaned

def graph(diz, distanza):
    
    '''Funzione che restituisce in tempo lineare un grafo quando le viene
    passata un dizionario ed una distanza per impostare gli archi.
    Il dizionario passato deve avere la sigla delle provincia come chiave e la
    tupla (latitudine, longitudine) come valori corrispondenti. Se si intende
    lavorare con il file .json fornito dal dipartimento della Protezione Civile è
    sufficiente pulire i dati con la funzione `data_cleaning(ls)`; se altrimenti
    si vuole procedere con una simulazione è necessario ricorrere alla funzione
    `casual_data(n)`. I vertici sono rappresentati dalle città e si traccia un
    arco tra di essi se ciò che segue è verificato: sia (x,y) la posizione di a,
    allora b è in posizione (z,w), con z in [x-d, x+d] e w in [y-d, y+d], con
    d = distanza.'''
    
    nomi = list(diz.keys())
    lat = [avalue[0] for avalue in diz.values()]
    long = [avalue[1] for avalue in diz.values()]
    
    var_lat = np.var(lat)
    var_long = np.var(long)
    
    G = nx.Graph()
        
    if var_lat > var_long:
        tuples = zip(*sorted(zip(lat, nomi, long)))
        lat, nomi, long = [list(tuple) for tuple in tuples]
        edges = []
        for i in range(len(nomi)):
            nome_i = nomi[i]
            G.add_node(nome_i, pos=(long[i], lat[i]))
            j = i + 1
            dist_lat = 0
            while dist_lat <= distanza and j < len(nomi): 
                dist_lat = lat[j] - lat[i] # non prendo il valore assoluto perché è un valore già positivo
                dist_long = abs(long[j] - long[i])
                nome_j = nomi[j]
                if dist_long <= distanza:
                    edges.append((nome_i, nome_j))
                j += 1
    else:
        tuples = zip(*sorted(zip(long, nomi, lat)))
        long, nomi, lat = [list(tuple) for tuple in tuples]
        edges = []
        for i in range(len(nomi)):
            nome_i = nomi[i]
            G.add_node(nome_i, pos=(long[i], lat[i]))
            j = i + 1
            dist_long = 0
            while dist_long <= distanza and j < len(nomi):
                dist_long = long[j] - long[i] # non prendo il valore assoluto perché è un valore già positivo
                dist_lat = abs(lat[j] - lat[i])
                nome_j = nomi[j]
                if dist_lat <= distanza:
                    edges.append((nome_i, nome_j))
                j += 1
                           
    G.add_edges_from(edges)            
    return G

dati_reali = data_cleaning(d)
P = graph(dati_reali, 0.8)

def setColor_flag(G):
    
    '''Funzione che prende in input un grafo e ritorna una lista di colori,
    ispirata ai colori della bandiera Italiana, sulla base della posizione x del
    nodo.
    - 1° terzile: Verde
    - 2° terzile: Bianco
    - 3° terzile: Rosso'''
    
    pos = nx.get_node_attributes(G, 'pos')
    nomi = list(pos.keys())
    long = [avalue[0] for avalue in pos.values()]
    lat = [avalue[1] for avalue in pos.values()]
    ma = max(long)
    mi = min(long)
    q = (ma - mi) / 3
    colors = {}
    for i in range(len(nomi)):
        y = long[i]
        if y >= mi and y < mi + q:
            colors[nomi[i]] = 'green'
        if y >= mi + q and y <= mi + 2*q:
            colors[nomi[i]] = 'white'    
        if y >= mi + 2*q and y <= mi + 3*q:
            colors[nomi[i]] = 'red'
    values = colors.values()
    return values

nx.draw(P, pos=nx.get_node_attributes(P, 'pos'), with_labels=True, node_size=150, font_size=8, node_color=setColor_flag(P))
plt.show()



def data_generating(n):
    
    '''Funzione che ritorna un dizionario di dati casuali di n città che hanno
    latitudine nell'intervallo [30, 50) e longitudine in [10, 20). 
    Il dizionario ritornato ha come chiavi il numero identificativo della città
    e come valori le tuple (latitudine, longitudine).'''   
    
    casual = {i: (30 + 20 * random.random(), 10 + 10 * random.random()) for i in range(n)}
    return casual

dati_casuali = data_generating(2000)
R = graph(dati_casuali, 0.08)

def setColor_degree(G):
    
    '''Funzione che prende in input un grafo e ritorna una lista di colori,
    ispirata ai colori del Triage, sulla base del grado del nodo.
    - Grado 0: Grigio
    - Grado 1: Verde
    - Grado 2: Azzurro
    - Grado 3: Giallo
    - Grado 4: Rosso
    - Grado 5: Nero'''

    degree = dict(R.degree)
    colors = {}
    for i in degree:
        if degree.get(i) == 0:
            colors[i] = 'gainsboro'
        if degree.get(i) == 1:
            colors[i] = 'green'
        if degree.get(i) == 2:
            colors[i] = 'cyan'
        if degree.get(i) == 3:
            colors[i] = 'yellow'
        if degree.get(i) == 4:
            colors[i] = 'red'
        if degree.get(i) == 5:
            colors[i] = 'black'
    values = [colors.get(node, 0) for node in R.nodes()]
    return values

nx.draw(R, pos=nx.get_node_attributes(R, 'pos'), node_size=20, node_color=setColor_degree(R))
plt.legend(['Triage colors'], loc=1)
plt.show()




def weighted_graph(diz, distanza):
    
    '''Funzione che restituisce in tempo lineare un grafo pesato quando le
    viene passata un dizionario ed una distanza per impostare gli archi.
    Il dizionario passato deve avere la sigla delle provincia come chiave e la
    tupla (latitudine, longitudine) come valori corrispondenti. Se si intende
    lavorare con il file .json fornito dal dipartimento della Protezione Civile
    è sufficiente pulire i dati con la funzione `data_cleaning(ls)`; se
    altrimenti si vuole procedere con una simulazione è necessario ricorrere
    alla funzione `casual_data(n)`. I vertici sono rappresentati dalle città e
    si traccia un arco tra di essi se ciò che segue è verificato: sia (x, y) la
    posizione di a, allora b è in posizione (z,w), con z in [x-d, x+d] e w in
    [y-d, y+d], con d = distanza.'''
    
    nomi = list(diz.keys())
    lat = [avalue[0] for avalue in diz.values()]
    long = [avalue[1] for avalue in diz.values()]
    
    var_lat = np.var(lat)
    var_long = np.var(long)
    
    G = nx.Graph()
    
    if var_lat > var_long:
        tuples = zip(*sorted(zip(lat, nomi, long)))
        lat, nomi, long = [list(tuple) for tuple in tuples]
        edges = []
        for i in range(len(nomi)):
            nome_i = nomi[i]
            G.add_node(nome_i, pos=(long[i], lat[i]))
            j = i + 1
            dist_lat = 0
            while dist_lat <= distanza and j < len(nomi): 
                dist_lat = lat[j] - lat[i] # non prendo il valore assoluto perché è un valore già positivo
                dist_long = abs(long[j] - long[i])
                nome_j = nomi[j]
                if dist_long <= distanza:
                    Eucl_dist = (dist_lat ** 2 + dist_long ** 2) ** (1/2)
                    edges.append((nome_i, nome_j, Eucl_dist))
                j += 1
    else:
        tuples = zip(*sorted(zip(long, nomi, lat)))
        long, nomi, lat = [list(tuple) for tuple in tuples]
        edges = []
        for i in range(len(nomi)):
            nome_i = nomi[i]
            G.add_node(nome_i, pos=(long[i], lat[i]))
            j = i + 1
            dist_long = 0
            while dist_long <= distanza and j < len(nomi):
                dist_long = long[j] - long[i] # non prendo il valore assoluto perché è un valore già positivo
                dist_lat = abs(lat[j] - lat[i])
                nome_j = nomi[j]
                if dist_lat <= distanza:
                    Eucl_dist = (dist_long ** 2 + dist_lat ** 2) ** (1/2)
                    edges.append((nome_i, nome_j, Eucl_dist))
                j += 1
                           
    G.add_weighted_edges_from(edges)            
    return G

weighted_P = weighted_graph(dati_reali, 0.8)
weighted_R = weighted_graph(dati_casuali, 0.08)




def eulerian_path(G):
    
    """Funzione che prende in input un grafo e che stabilisce, in primis, se
    questo è Euleriano, e, se questo è verificato, ritorna il cammino euleriano.
    La funzione è implementata secondo l'algoritmo di Fleury."""
    
    CC = list(nx.connected_components(G))
    CC_count = 0
    for c in CC:
        if len(c) != 1:
            CC_count += 1
    if CC_count != 1:
        return 'This graph is not Eulerian nor semi-Eulerian.'
    
    edges = G.edges
    degree = G.degree    
    nodes = list(G.nodes)
    
    odd_degree_nodes = 0
    odd_list = []
    for anode in nodes:
        if degree[anode] % 2 != 0:
            odd_degree_nodes += 1
            odd_list.append(anode)
            
    edge_path = []
    if odd_degree_nodes == 2:
        next_node = odd_list[random.randint(0, len(odd_list)-1)]
        while edges:
            current_node = next_node
            node_edges = list(edges(current_node))
            arandom = random.randint(0, len(node_edges)-1)
            edge = node_edges[arandom]
            if not is_bridge(edge, G):
                edge_path.append(current_node)
                next_node = edge[1]
                G.remove_edge(*edge)
        edge_path.append(next_node)
        return edge_path
      
    elif odd_degree_nodes == 0:
        next_node = nodes[random.randint(0, len(nodes)-1)]
        while edges:
            current_node = next_node
            node_edges = list(edges(current_node))
            arandom = random.randint(0, len(node_edges)-1)
            edge = node_edges[arandom]
            if not is_bridge(edge, G):
                edge_path.append(current_node)
                next_node = edge[1]
                G.remove_edge(*edge)
        edge_path.append(next_node)
        return edge_path
    
    else:
        return 'This graph is not Eulerian nor semi-Eulerian.'
    
def is_bridge(edge, G):
    
    """Funzione ausiliaria all'algoritmo di Fleury che stabilisce se un arco è
    un ponte oppure no. Prende in input l'arco stesso ed il grafo interessato."""
    
    H = G.copy()
    next_node = edge[0]
    i = dfs(next_node, H) - 1
    H.remove_edge(*edge)
    j = dfs(next_node, H) - 1
    if i == j or j == 0:
        return False
    return True

def dfs(next_node, G):
    
    '''Funzione di Depth First Search (DFS).'''
    
    nodes = list(G.nodes())
    colors = {anode: 'white' for anode in nodes}
    return visit(next_node, colors, G)

def visit(current, colors, G, count=0):
    
    '''Funzione ausiliara alla DFS.'''
    
    count += 1
    colors[current] = 'grey'
    adj = list(G.adj[current])
    for anode in adj:
        if colors[anode] == 'white':
            count = visit(anode, colors, G, count)
    return count

P = graph(dati_reali, 0.8)
print(eulerian_path(P))

R = graph(dati_casuali, 0.08)
print(eulerian_path(R))

K = nx.Graph()
K.add_nodes_from([0, 1, 2, 3, 4, 5])
K.add_edges_from([(0, 1), (0, 5), (1, 2), (1, 4), (2, 3), (2, 4), (2, 5), (3, 4)])
nx.draw_shell(K, with_labels=True)
print(eulerian_path(K))

Q = nx.Graph()
Q.add_nodes_from([0, 1, 2, 3, 4, 5])
Q.add_edges_from([(0, 1), (0, 3), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4), (3, 5), (4, 5)])
pos = {0: (0, 0), 1: (0.5, 0), 2: (1, 0), 3: (0, 4), 4: (1, 4), 5: (0.5, 8)}
nx.draw(Q, pos=pos, with_labels=True)
print(eulerian_path(Q))




def degree_distribution(G):
    
    '''Funzione che prende in input un grafo e ritorna un vocabolario che ha
    come chiavi i gradi e come valori le frequenze.'''
    
    degree = dict(G.degree)
    degree_list = list(degree.values())
    degree_voc = {adegree: None for adegree in degree_list} # faccio un vocabolario in modo da eliminare tutti i doppioni (mi costa O(n))
    degree_list_ = [adegree for adegree in degree_voc] # riconverto tutto in lista
    degree_list_.sort() # ordino la lista (mi costa(O(n*log(n)))
    n = len(degree)
    freq = [0]*(max(degree_list_)+1)
    for i in degree_list:
        freq[i] = freq[i] + 1
    distr_dict = {}
    for i in degree_list_:
        distr_dict[i] = freq[i] / n
    return distr_dict

def freq(G, k):
    
    '''Funzione che prende in input un grafo ed un grado e ritorna la rispettiva
    frequenza'''
    
    return degree_distribution(G).get(k)

print(degree_distribution(P))
print(degree_distribution(R))

def exponent_power_law(G, xmin=1):
    
    """Funzione che prende in input un grafo ed un x minimo (grado minimo da cui
    si vuole partire per la stima) e ritorna una stima dell'esponente della
    power law.
    xmin > 0, default=1."""
    
    deg = list(dict(G.degree).values())
    x = []
    for el in deg:
        if el >= xmin:
            x.append(el)
    n = len(x)
    intervallo = []
    for i in range(1, 1001):
        q = 1 + 6*i/1000
        intervallo.append(q)
    LL = {}
    for alfa in intervallo:
        zeta = 0
        for i in range(10000):
            zeta = zeta + (i + xmin) ** (-alfa)
        likelihood = -n*zeta - alfa*sum(np.log(x))
        LL[alfa] = likelihood
        
    alfa_hat = max(LL, key=LL.get)
    return alfa_hat

print(exponent_power_law(P, 1))
print(exponent_power_law(P, 7))
print(exponent_power_law(R, 1))