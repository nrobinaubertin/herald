<h1 align="center">
Herald
<br/>
<img align="center" src="herald.webp">
</h1>
<h4 align="center">Chess engine written in python</h4>

## Why ?

For fun.  
But more seriously, the goal of this engine is later to be able to play
all kind of faery chess variants, not only the standard variation.  
I want it to only use the standard modules of python.

## What is implemented for now ?

It uses alpha-beta pruning with move ordering
and a simple transposition table. Its evaluation function
is based on material and piece-square tables.  
It is mono-threaded for now.

## Zipapp

You can create a zipapp with the following command:

```sh
python3 -m zipapp src \
  -o "herald-$(git log -n1 --format=%h).pyz" \
  -p "/usr/bin/env python3"
```

## Run a test suite

You can run a test suite by using the following command:

```sh
python3 -m unittest tests/<test_name>
```
