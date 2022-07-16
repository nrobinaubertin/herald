<h1 align="center">
Herald
<br/>
<img align="center" src="herald.webp">
</h1>
<h4 align="center">Chess engine written in python</h4>

## Why ?

For fun.  
But more seriously, the goal of this engine is later to be able to play all kind of faery chess variants, not only the standard variation.  
I want it to only use the standard modules of python.

## What is implemented for now ?

It uses alpha-beta pruning with move ordering and a simple transposition table. Its evaluation function is based on material, piece-square tables.  
I want to enhance this with some SSE, mobility evaluation, iterative deepening and aspiration windows (work in progress !)  
I will also improve the PST and material evaluation with genetic algorithms.
