import sys

import networkx as nx
from node import QNode
from BB84_run import run_BB84_sim

def generateTestGraph():
    G = nx.Graph()

    G.add_node(0, qnode=QNode())
    
    for i in range(1, 5):
        G.add_node(i, qnode=QNode())
        G.add_edge(i-1, i, weight = 10) # weight = distance between node in network

    nx.draw(G)
    
    return G

'''
Assumes that consecutive nodes in nodes are connected with edges

returns time, compromised
'''
def generateRunOnPath(nodes, graph):
    compromisedRun = False
    elapsedTime = 0
    
    for i in range(0, len(nodes) - 1):
        connectionLength = graph.edges[nodes[i], nodes[i+1]]['weight']

        MyKeyList_A, MyKeyList_B, MyKeyRateList, ElapsedTimes = run_BB84_sim(fibreLen=connectionLength, fibreNoise=10**5)

        elapsedTime += ElapsedTimes[0]

        if graph.nodes[nodes[i]]['qnode'].isCompromised():
            compromisedRun = True

        if graph.nodes[nodes[i+1]]['qnode'].isCompromised():
            compromisedRun = True
        
        
    return elapsedTime, compromisedRun

def graphFromEdgeFile(filepath, default_weight=None, force_int=False):

    G = nx.Graph()
    my_nodes = set()

    with open(filepath, 'r', encoding='utf-8') as fp:

        for line in fp:

            splitted = line.strip().split()
            if len(splitted) <= 1:

                continue

            if len(splitted) == 2:

                assert default_weight is not None

                u, v = splitted
                weight = default_weight

            else:

                u, v, weight = splitted[:3]
                weight = int(weight)

            if force_int:

                u = int(u)
                v = int(v)

            if u not in my_nodes:

                G.add_node(u, qnode=QNode())
                my_nodes.add(u)

            if v not in my_nodes:

                G.add_node(v, qnode=QNode())
                my_nodes.add(v)

            G.add_edge(u, v, weight=weight)

    return G

if __name__ == "__main__":

    if len(sys.argv) > 1:

        G = graphFromEdgeFile(sys.argv[1])

    else:

        G = generateTestGraph()

    time, compromised = generateRunOnPath([0, 1, 2, 3, 4], G)

    print(time)
    print(compromised)

    while True:
        pass
        
