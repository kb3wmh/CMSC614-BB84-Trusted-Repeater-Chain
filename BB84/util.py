import logging
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)

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
