# Nethealth Tooling

## Dependencies
1. Python 3.6 or newer
2. python-igraph
3. numpy
4. matplotlib
5. (DEPRECIATED) Networkx
6. (DEPRECIATED) Pandas

## Setup
1. Download Dependencies - Use the provided requirements.txt
2. For graph.py, visual.py, and visual_text.py, make sure that the files dictionary is specified correctly or that 
the files are passed in via arguments, depending on the file being executed.
3. NOTE: Run visual_text.py to test the code, as this is the test that is run on the remote compute cluster (Ganxis)

## Usage
visual_text.py COMMUNICATION_DATA_FILENAME BASIC_SURVEY_DATA_FILENAME NETWORK_SURVEY_DATA_FILENAME 

## Files
1. GraphClasses.py - contains needed storage classes for the Networkx Graph
2. graph.py - contains helper and test functions that perform graph-specific analysis on the data
3. visual.py - Graph Based Visualizations
4. visual_text.py - Text Based Visualizations
5. loader2.py - loads data directly from files and contains an enum that describes the index values of the comm event data
6. (DEPRECIATED) graph_networkx.py - NetworkX implementation of graph.py
7. (DEPRECIATED) loader.py - older version of data loading. Contains functions to perform past analysis
8.  (DEPRECIATED) pandas_load.py - contains logic to open and load data as well as some testing functions

For Further Documentation, see the function docstrings and comments for further details
