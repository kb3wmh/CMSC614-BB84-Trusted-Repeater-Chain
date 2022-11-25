"""
This is meant to be run as script!
"""

import sys

from network import graphFromEdgeFile
from util import all_simple_not_improvable_paths

assert len(sys.argv) > 3

G = graphFromEdgeFile(sys.argv[1])
source = sys.argv[2]
target = sys.argv[3]

for path in all_simple_not_improvable_paths(G, source, target):

	print(path)
