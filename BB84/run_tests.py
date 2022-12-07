import csv
from network import calculateNonImprovableFractions

if __name__ == "__main__":
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
