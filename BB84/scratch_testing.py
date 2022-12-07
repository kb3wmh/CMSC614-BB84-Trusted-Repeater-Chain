from util import *
from network import *
import matplotlib.pyplot as plt

if __name__ == "__main__":
    G = graphFromRandom(50, 4/49, 999999999999, seed=77777)

    nonImprovableFromGenerator = list(all_simple_not_improvable_paths_using_dfs(G, 1, 2))

    print(len(nonImprovableFromGenerator))

    plotGraphWithPathHighlighted(G, paths=nonImprovableFromGenerator)
    plt.show()
