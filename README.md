# Nethealth Tooling

## Dependencies
1. Python 3.7 or newer
2. (DEPRECIATED) Networkx
3. python-igraph
3. (DEPRECIATED) Pandas

## Setup
1. Download Dependencies
2. Set the files dictionary object in the pandas_load.py file to the places where the data is stored

## Files
2. GraphClasses.py - contains needed storage classes for the Networkx Graph
3. graph.py - contains helper and test functions that perform graph-specific analysis on the data
4. visual.py - Graph Based Visualizations
5. visual_text.py - Text Based Visualizations
6. loader2.py - loads data directly from files and contains an enum that describes the index values of the comm event data
6. (DEPRECIATED) graph_networkx.py - NetworkX implementation of graph.py
7. (DEPRECIATED) loader.py - older version of data loading. Contains functions to perform past analysis
8  (DEPRECIATED) pandas_load.py - contains logic to open and load data as well as some testing functions

For Further Documentation, see the function docstrings and comments for further details
