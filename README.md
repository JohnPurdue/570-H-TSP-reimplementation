# README
## Project
*reimplementing [this H-TSP paper](https://github.com/Learning4Optimization-HUST/H-TSP )*

This project isn't really complete as I was unable to finish in time.

## Contents

### Solutions

Contains comparisons from a few solvers I ran., mostly the naive solution of taking all modes in order, and the results from gradually adding other fatures.

### Data

Contains data from TSPLIB, the .tar file is everything, but there are only a few unziped files I added so that the code can run. 

The .gpickle files have been formatted using NetworkX, which is a library used for analyzing graph data that the project uses.

### SRC

preprocess.py is how we normalize the data and create the .gpickle files that are used in the main implementation.

solveTSP.py is the "main" file here and it calls all the other necessary functions and files.

### MISC

The repo also conatins an html file of a flowchart, which explains the overall project dataflow, a documentation pdc for using TSPLIB for reference during building, and a pdf of the term paper that goes along with this code.
