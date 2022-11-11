# cr-data-mining
This repository contains a program that, given a list of *players tags*, obtains it recent *battlelog* (set of battles played). In this game, we can clasificate matches by number of players: *1vs1* or *2vs2*. In this case, it is only considered the individual games (*1vs1*), regardless the battle type (*draft*, *clanWar*, *ladder*, etc).

To use it, you must provide 2 files (by program args *-p* and *-t*, respectively):
- a file that contains the *tags*, separated by spaces (i.e. *tags.txt*)
- a file that contains the *API token* (copy and paste it in a blank file).

To get an *API token*, you must be registered at [this site](https://developer.clashroyale.com/).

This program can be used to store dinamically the battles, given that it writes the battles data as a formatted string (*csv*) in an specified file (arg *-o*, default *output.csv*). If file contains previous data, only new battles are added to the file.

## Execution example
- (On Windows) python.exe .\battles_mining.py -p tags.txt -t .\token.txt -o data.csv
- (On Linux) python battles_mining.py -p tags.txt -t token.txt -o data.csv

## Libraries required
The set of libraries needed to run is:
1. *asyncio*, *aiohttp* and *json* for the *http requests*
2. *pandas* for *data manipulation*
