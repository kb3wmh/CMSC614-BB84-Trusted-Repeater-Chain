import random
import sys

import networkx as nx
import matplotlib.pyplot as plt
from node import QNode
from BB84_run import run_BB84_sim
import math


'''
All paths
All non-improvable paths

k Randomly selected non-improvable paths

"fancy algorithms"
'''


def generateTestGraph():
    G = nx.Graph()

    G.add_node(0, qnode=QNode())
    
    for i in range(1, 5):
        G.add_node(i, qnode=QNode())
        G.add_edge(i-1, i, weight = 10) # weight = distance between node in network
    
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

def graphFromRandom(n, p, patience, seed=123456789):
    """
    n : int
        number of nodes
    p : float
        fraction between 0 and 1 that determines how likely an edge is to be kept
    patience: int
        how many disconnected graphs are encountered before quitting
    seed : int
        used to make the function deterministic
    """

    assert patience > 0

    random.seed(seed)

    facade_G = nx.freeze(nx.complete_graph(n))
    G = nx.Graph(facade_G)

    disconnected = 0
    for u, v in facade_G.edges:

        if p <= random.random():

            G.remove_edge(u, v)
            if not nx.is_connected(G):

                G.add_edge(u, v)

                disconnected += 1
                if disconnected >= patience:

                    break

    return G

def plotGraphWithPathHighlighted(G, paths=None, pos=None):
    if (pos == None):
        pos=nx.kamada_kawai_layout(G)

    nx.draw_networkx_nodes(G, pos=pos)
    nx.draw_networkx_labels(G, pos=pos)
    
    arcs = nx.draw_networkx_edges(G, pos=pos)

    if (paths != None):
        for path in paths:
            edgelist = []
        
            for i in range(0, len(path)-1):
                edgelist.append((path[i], path[i+1]))

            nx.draw_networkx_edges(G, pos, edgelist=edgelist, width=8, alpha=0.5, edge_color="tab:red")
    
    plt.savefig('graph.png')



def updateWeightsUsingLayout(G, pos, minDistKm=1, maxDistKm=10):
    minGraphDist = math.inf
    maxGraphDist = -1

    for nodeA, nodeB in G.edges():
        posA = pos[nodeA]
        posB = pos[nodeB]

        dist = math.sqrt((posA[0] - posB[0])**2 + (posA[1] - posB[1])**2)

        G.edges[nodeA, nodeB]['weight'] = dist

        if (dist > maxGraphDist):
            maxGraphDist = dist

        if (dist < minGraphDist):
            minGraphDist = dist

    slope = (maxDistKm - minDistKm)/(maxGraphDist - minGraphDist)
    transform = lambda x: slope * (x - minGraphDist) + minDistKm

    for nodeA, nodeB in G.edges():
        G.edges[nodeA, nodeB]['weight'] = transform(G.edges[nodeA, nodeB]['weight'])


def compromiseNodes(G, numToCompromise):
    for node in G.nodes:
        G.nodes[node]['qnode'] = QNode()


    for node in random.sample(G.nodes, numToCompromise):
        G.nodes[node]['qnode'].compromise()

        
def testForCompromisedKey(G, paths):
    for path in paths:
        compromisedPath = False
        
        for node in path:
            if G.nodes[node]['qnode'].isCompromised():
                compromisedPath = True
                break

        if not compromisedPath:
            return False

    return True

def generateSimplePaths(G, startNode, endNode, numToGenerate=math.inf):
    pathGenerator = nx.all_simple_paths(G, startNode, endNode)
    paths = []
    count = 0

    for path in pathGenerator:
        if count > numToGenerate:
            break
        
        paths.append(path)
        count += 1

    return paths

def randomlySelectPaths(paths, num):
    return random.sample(paths, num)

def generateNonImprovablePaths(G, paths):
    improvedPaths = []

    for path in paths:
        i = 0
        isImprovable = False
        
        for node in path:
            for edge in G.edges(node):
                if edge[1] in path[i+2:]:
                    isImprovable = True
                    break

            i += 1
            
            if isImprovable:
                break

        if not isImprovable:
            improvedPaths.append(path)

    return improvedPaths
                    


if __name__ == "__main__":
    
    if len(sys.argv) > 3:

        G = graphFromEdgeFile(sys.argv[1])
        test_path = next(nx.all_simple_paths(G, sys.argv[2], sys.argv[3]))

    else:

        G = generateTestGraph()
        test_path = [0, 1, 2, 3, 4]

    time, compromised = generateRunOnPath(test_path, G)

    print(time)
    print(compromised)

    for i in range(1):
        randGraph = graphFromRandom(50, .03, 999999999999, seed=77)

        pos = nx.kamada_kawai_layout(randGraph)

        paths=generateSimplePaths(randGraph, 16, 34)

        plotGraphWithPathHighlighted(randGraph, pos=pos, paths=paths)

        updateWeightsUsingLayout(randGraph, pos)
        compromiseNodes(randGraph, 5)

        print(generateNonImprovablePaths(randGraph, paths))
        
        print(testForCompromisedKey(randGraph, paths))
        
        


    plt.show()
        
    print("Done")
        
