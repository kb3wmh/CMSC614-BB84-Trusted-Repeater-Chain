import networkx as nx
from node import QNode
from BB84_run import run_BB84_sim

def generateTestGraph():
    G = nx.Graph()

    G.add_node(0, qnode=QNode())
    
    for i in range(1, 5):
        G.add_node(i, qnode=QNode())
        G.add_edge(i-1, i, weight = 10**-9) # weight = distance between node in network

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

        MyKeyList_A, MyKeyList_B, MyKeyRateList, ElapsedTimes = run_BB84_sim()

        elapsedTime += ElapsedTimes[0]

        if graph.nodes[nodes[i]]['qnode'].isCompromised():
            compromisedRun = True

        if graph.nodes[nodes[i+1]]['qnode'].isCompromised():
            compromisedRun = True
        
        
    return elapsedTime, compromisedRun

if __name__ == "__main__":
    G = generateTestGraph()

    time, compromised = generateRunOnPath([0, 1, 2, 3, 4], G)

    print(time)
    print(compromised)
        
