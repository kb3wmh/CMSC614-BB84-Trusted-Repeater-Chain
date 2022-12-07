import csv
from network import *
from util import *
from node import QNode

def test_all_vs_simple_fractions():
    outputCSVFilename = "test2.csv"
    heading = ['Number of Nodes',
               'Average Fraction',
               'Average Number of Simple Paths',
               'Average Number of Non-Improvable Paths']

    minNodes = 21
    maxNodes = 22

    averageFractions, averageSimplePaths, averageNonImprovablePaths = calculateNonImprovableFractions(minNodes, maxNodes)
    
    print(averageFractions)
    print(averageSimplePaths)
    print(averageNonImprovablePaths)

    with open(outputCSVFilename, 'w', newline='') as csvfile:
        resultWriter = csv.writer(csvfile)

        resultWriter.writerow(heading)

        for i in range(minNodes, maxNodes + 1):
            nextIndex = i - minNodes
            nextRow = [i, averageFractions[nextIndex], averageSimplePaths[nextIndex], averageNonImprovablePaths[nextIndex]]

            resultWriter.writerow(nextRow)



def test_security_nonimprovable():
    minNodes = 5
    maxNodes = 20
    numTrials = 1000

    heading = ["Num Nodes", ".05", ".10", ".15", ".20"]

    result = []

    for node in range(minNodes, maxNodes + 1):
        print("Number of nodes: " + str(node))
        compromiseProbabilities = [node]
        
        for compromiseProbability in range(5, 25, 5):
            compromiseCount = 0
        
            for i in range(0, numTrials):
                G = graphFromRandom(node, 4/(node-1), 99999999999, seed=(node + compromiseProbability + i))
                targetNodes = random.sample(G.nodes(), 2)
                
                compromiseNodesWithProbabilityP(G, compromiseProbability/100, targetNodes[0], targetNodes[1])
                
                nonImprovable = all_simple_not_improvable_paths_using_dfs(G, targetNodes[0], targetNodes[1])
                
                if testForCompromisedKey(G, nonImprovable):
                    compromiseCount += 1

            compromiseProbabilities.append(compromiseCount / numTrials)

        result.append(compromiseProbabilities)

    outputCSVFilename = "test_security_nonimprovable.csv"

    with open(outputCSVFilename, 'w', newline='') as csvfile:
        resultWriter = csv.writer(csvfile)
        resultWriter.writerow(heading)

        for row in result:
            resultWriter.writerow(row)



def test_security_nonimprovable_sample():
    minNodes = 5
    maxNodes = 20
    numTrials = 1000
    numPaths = 5

    heading = ["Num Nodes", ".05", ".10", ".15", ".20"]

    result = []

    for node in range(minNodes, maxNodes + 1):
        print("Number of nodes: " + str(node))
        compromiseProbabilities = [node]
        
        for compromiseProbability in range(5, 25, 5):
            compromiseCount = 0
        
            for i in range(0, numTrials):
                G = graphFromRandom(node, 4/(node-1), 99999999999, seed=(node + compromiseProbability + i))
                targetNodes = random.sample(G.nodes(), 2)
                
                compromiseNodesWithProbabilityP(G, compromiseProbability/100, targetNodes[0], targetNodes[1])
                
                nonImprovable = list(all_simple_not_improvable_paths_using_dfs(G, targetNodes[0], targetNodes[1]))

                if numPaths < len(nonImprovable):
                    pathsSample = random.sample(nonImprovable, numPaths)

                else:
                    pathsSample = nonImprovable
                
                if testForCompromisedKey(G, pathsSample):
                    compromiseCount += 1

            compromiseProbabilities.append(compromiseCount / numTrials)

        result.append(compromiseProbabilities)

    outputCSVFilename = "test_security_nonimprovable_sample.csv"

    with open(outputCSVFilename, 'w', newline='') as csvfile:
        resultWriter = csv.writer(csvfile)
        resultWriter.writerow(heading)

        for row in result:
            resultWriter.writerow(row)

        
            
            
if __name__ == "__main__":
    test_security_nonimprovable_sample()
    
