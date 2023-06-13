<h1 align="center">
Herald
<br/>
<img align="center" src="herald.webp" title="Herald reading his script">
</h1>
<h4 align="center">Chess engine written in python</h4>

## Why ?

For fun.  
I've written a blog post detailing the story of this chess engine
that you can read [here](http://niels.fr/blog/starting-my-own-chess-engine/).

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
  -p "/usr/bin/env -S python3 -O"
```

## Run the tests

You can run the tests by using the following command:

```sh
tox
```
