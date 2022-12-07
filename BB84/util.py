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

def path_not_improvable_using_sets(G, path):
    """
    This function assumes path[i] and path[i + 1] are connected.
    """

    grand_inquisitor = set()

    for i in range(2, len(path)):

        grand_inquisitor |= set(G[path[i - 2]])

        if path[i] in grand_inquisitor:

            return False

    return True

def all_simple_not_improvable_paths(G, source, target, cutoff=None):
    """
    Returns a generator that produces not improvable paths. 
    """

    return (path for path in
            nx.all_simple_paths(G, source=source, target=target, cutoff=cutoff)
            if path_not_improvable(G, path))

def all_simple_not_improvable_paths_using_sets(G, source, target, cutoff=None):

    return (path for path in
            nx.all_simple_paths(G, source=source, target=target, cutoff=cutoff)
            if path_not_improvable_using_sets(G, path))

def all_simple_not_improvable_paths_using_dfs(G, source, target, cutoff=None):
    """
    This function is a GENERATOR.
    It does not return anything.
    Usage: list(all_simple_not_improvable_paths_using_dfs(...))
    """

    curr_path = OrderedDict.fromkeys([source])

    unvisited_neighbors = set(G[source])
    do_not_visit = unvisited_neighbors.copy()
    stack = [(unvisited_neighbors, do_not_visit)]

    while stack:

        unvisited_neighbors, do_not_visit = stack[-1]

        if not unvisited_neighbors or (cutoff is not None and len(stack) - 1 <= cutoff):

            curr_path.popitem()
            stack.pop()
            continue

        neighbor = unvisited_neighbors.pop()

        # don't do a loopdy loop
        if neighbor in curr_path:

            continue

        if neighbor == target:

            yield tuple(curr_path.keys()) + (target, )
            continue

        curr_path[neighbor] = None

        neighbor_neighbors = set(G[neighbor])
        stack.append((
            list(neighbor_neighbors - do_not_visit), do_not_visit | neighbor_neighbors
        ))

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

def node_not_taken(G, source, target, k):
    """
    Returns a tuple (success, path_set).
    """

    visits = dict.fromkeys(G.nodes, 0)
    # priority if target is a neighbor
    visits[target] = -1

    def dfs():

        curr_path = OrderedDict.fromkeys([source])

        unvisited_neighbors = set(G[source])
        do_not_visit = unvisited_neighbors.copy()
        stack = [(unvisited_neighbors, do_not_visit)]

        while stack:

            unvisited_neighbors, do_not_visit = stack[-1]

            if not unvisited_neighbors:

                curr_path.popitem()
                stack.pop()
                continue

            neighbor = min(unvisited_neighbors, key=lambda x : visits[x])

             # lower bound is at least 2 => we can ignore all neighbors
            if visits[neighbor] >= 2:

                curr_path.popitem()
                stack.pop()
                continue

            unvisited_neighbors.remove(neighbor)

            # don't do a loopdy loop
            if neighbor in curr_path:

                continue

            if neighbor == target:

                the_path = tuple(curr_path.keys())

                for node in the_path:

                    visits[node] += 1

                # don't update visits for target to keep it a priority
                return the_path + (target, )

            curr_path[neighbor] = None

            neighbor_neighbors = set(G[neighbor])
            stack.append((
                neighbor_neighbors - do_not_visit, do_not_visit | neighbor_neighbors
            ))

        return None

    path_list = []
    for _ in range(k):

        the_path = dfs()

        if the_path is None:

            return False, set(path_list)

        path_list.append(the_path)

    path_set = set(path_list)
    return len(path_set) == k, path_set

def node_less_traveled(G, source, target, k):
    """
    Returns a tuple (success, path_set).
    """

    visits = dict.fromkeys(G.nodes, 0)
    # priority if target is a neighbor
    visits[target] = -1

    def dfs():

        curr_path = OrderedDict.fromkeys([source])

        unvisited_neighbors = set(G[source])
        do_not_visit = unvisited_neighbors.copy()
        stack = [(unvisited_neighbors, do_not_visit)]

        while stack:

            unvisited_neighbors, do_not_visit = stack[-1]

            if not unvisited_neighbors:

                curr_path.popitem()
                stack.pop()
                continue

            neighbor = min(unvisited_neighbors, key=lambda x : visits[x])
            unvisited_neighbors.remove(neighbor)

            # don't do a loopdy loop
            if neighbor in curr_path:

                continue

            if neighbor == target:

                the_path = tuple(curr_path.keys())

                for node in the_path:

                    visits[node] += 1

                # don't update visits for target to keep it a priority
                return the_path + (target, )

            curr_path[neighbor] = None

            neighbor_neighbors = set(G[neighbor])
            stack.append((
                neighbor_neighbors - do_not_visit, do_not_visit | neighbor_neighbors
            ))

        return None

    path_list = []
    for _ in range(k):

        the_path = dfs()

        if the_path is None:

            return False, set(path_list)

        path_list.append(the_path)

    path_set = set(path_list)
    return len(path_set) == k, path_set
