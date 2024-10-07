# Shared Graph Reconstruction Playground

## Overview
Exploring the idea of reconstructing an original graph `G` from two graphs `A` and `B` derived by a `node-split` operation.  

The `node-split` operation is an iterative mutation process. `A` and `B` are identical to `G` at first. For each node `v` in `G`, the corresponding node `v` in one graph chosen at random between `A` and `B` is selected for splitting. Splitting a node means creating *N* new nodes with *mostly* the same parents and children that `v` has, and removing `v` from the graphs afterwards.  

The goal is to figure out whether it's possible to find the original graph `G` from the derived pair `A` and `B`. 
