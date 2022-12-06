from collections import OrderedDict
import logging
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)

import networkx as nx

'''
Compare two basis list, find the unmatched index, 
    then append the matched value from a list corresponded to the index.
Input:
    basis1: local basis used for measuring qubits.(list of int)
    basis2: remote basis used for measuring qubits.(list of int)
        
    sourceList2: Local measurement results(B) or state index(A).(list of int)
Output:
    Two new lists for further algorithm.
    And a list of value A or B when X=Y=1.
    Reference to https://wiki.veriqloud.fr/index.php?title=BB84_Quantum_Key_Distribution phase 2.
'''

def BB84_CompareBasis_old(basis1,basis2,sourceList2):
    targetList1=[]
    targetList2=[]
    ABoutput=[]

    if len(basis1) != len(basis2):
        mylogger.error("Comparing error! length of basis does not match! \n")
        mylogger.error("\nbasis1:{}\nbasis2:{}".format(basis1,basis2))
        return -1

    for i in range(len(basis1)):
        if basis1[i] == basis2[i]:
            targetList1.append(basis1[i])
            targetList2.append(sourceList2[i])
            if basis1[i]==1:
                ABoutput.append(sourceList2[i])

    return targetList1, targetList2, ABoutput


'''
Compare two basis list, find the unmatched index, 
    then append the matched value from a list corresponded to the index.
Input:
    basis1: local basis used for measuring qubits.(list of int)
    basis2: remote basis used for measuring qubits.(list of int)
    sourceList2: Local measurement results(B) or state index(A).(list of int)
Output:
    Keys in this party.
'''


def BB84_CompareBasis(basis1,basis2,sourceList2):

    key=[]
    if len(basis1) != len(basis2):
        mylogger.error("Comparing error! length of basis does not match! \n")
        mylogger.error("\nbasis1:{}\nbasis2:{}".format(basis1,basis2))
        return -1

    for i in range(len(basis1)):
        if basis1[i] == basis2[i]:
            key.append(sourceList2[i])

    return key

def path_not_improvable(G, path):

    for i in range(0, len(path) - 2):

        neighbors = G[path[i]]

        for j in range(i + 2, len(path)):

            if path[j] in neighbors:

                return False

    return True

def all_simple_not_improvable_paths(G, source, target, cutoff=None):
    """
    Returns a generator that produces not improvable paths. 
    """

    return (path for path in
            nx.all_simple_paths(G, source=source, target=target, cutoff=cutoff)
            if path_not_improvable(G, path))

def make_path_not_improvable(G, path):

    ni_path = [path[0]]

    i = 0
    while i < len(path) - 1:

        neighbors = G[path[i]]
        # reversal very important
        for j in reversed(range(i + 2, len(path))):

            if path[j] in neighbors:

                i = j - 1
                break

        i += 1
        ni_path.append(path[i])

    return ni_path

def node_not_taken(G, source, target, k, fast_fail=False):
    """
    fast_fail : bool
        If true, then function returns (success, latest path_set).
        Else this function returns path_set (same as node_less_traveled).
        False by default.
    """

    path_set = set()

    visits = dict.fromkeys(G.nodes, 0)
    # priority if target is a neighbor
    visits[target] = -1
    curr_path = OrderedDict.fromkeys([source])
    stack = [list(G[source])]

    while stack:

        neighbors = stack[-1]

        if not neighbors:

            curr_path.popitem()
            stack.pop()
            continue

        # visits may have changed further down in the graph
        a_neighbor = min(neighbors, key=lambda x : visits[x])

        # lower bound is at least 2 => we can ignore all neighbors
        if visits[a_neighbor] >= 2:

            # TODO: I'm not sure if this is intended
            if fast_fail:

                return False, path_set 

            curr_path.popitem()
            stack.pop()
            continue

        neighbors.remove(a_neighbor)

        # don't do a loopdy loop
        if a_neighbor in curr_path:

            continue

        if a_neighbor == target:

            ni_path = tuple(make_path_not_improvable(G, list(curr_path.keys()) + [target]))

            if any(visits[node] >= 2 for node in ni_path[1:-1]):

                if fast_fail:

                    return False, path_set 

                continue

            if ni_path in path_set:

                continue

            # don't update visits for target to keep it a priority
            for node in ni_path[:-1]:

                visits[node] += 1

            path_set.add(ni_path)
            if len(path_set) >= k:

                break

            continue

        curr_path[a_neighbor] = None
        stack.append(list(G[a_neighbor]))

    if fast_fail:

        return len(path_set) == k, path_set

    return path_set

def node_less_traveled(G, source, target, k):

    path_set = set()

    visits = dict.fromkeys(G.nodes, 0)
    # priority if target is a neighbor
    visits[target] = -1

    def dfs():

        curr_path = OrderedDict.fromkeys([source])
        curr_path_frontier = set()
        stack = [(set(G[source]), set())]

        while stack:

            neighbors = stack[-1][0]

            if not neighbors:

                curr_path.popitem()
                curr_path_frontier -= stack[-1][1]
                stack.pop()
                continue

            parent_neighbors = neighbors.copy()

            # visits may have changed further down in the graph
            a_neighbor = min(neighbors, key=lambda x : visits[x])
            neighbors.remove(a_neighbor)

            # don't do a loopdy loop
            if a_neighbor in curr_path:

                continue

            if a_neighbor == target:

                the_path = tuple(curr_path.keys())

                for node in the_path:

                    visits[node] += 1

                # don't update visits for target to keep it a priority
                return the_path + (target, )

            curr_path[a_neighbor] = None
            curr_path_frontier |= parent_neighbors
            stack.append((set(G[a_neighbor]) - curr_path_frontier, parent_neighbors))

        return None

    i = 0
    while i < k:

        the_path = dfs()

        if the_path is None:

            return False, path_set

        if the_path in path_set:

            continue

        path_set.add(the_path)
        i += 1

    return True, path_set
