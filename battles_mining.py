# Async request uses 
import asyncio
import aiohttp
import json

import argparse
import pandas as pd
import io

# Async requests
async def fetch(url, session):
    async with session.get(url) as response:
        return await response.read()

async def run(players, dst, headers):
    url = "https://api.clashroyale.com/v1/players/%23{}/battlelog"
    tasks = []

    # Limit rate
    connector = aiohttp.TCPConnector(limit=15)

    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        for i in range(len(players)):
            task = asyncio.ensure_future(fetch(url.format(players[i]), session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        
        for item in responses:
            for b in json.loads(item):
                dst.append(parse_battle(b))
            

def async_request(tags, token, dst):
    
    headers = {
    'Authorization' : "Bearer " + token
    }

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(run(tags, dst, headers))
    except KeyboardInterrupt:
        pass

# Keys to filter response
relevant_keys = ['type', 'battleTime', 'gameMode', 'team', 'opponent']
player_keys = ['name', 'tag', 'crowns', 'cards']
card_keys = ['name']

def parse_battle(data):
    btype, time, mode, team, op = [data[k] for k in relevant_keys]
    # No tracking 2vs2 and other colaborative modes
    if len(team) > 1: return None
    # Get values from keys for player and opponent
    team_info = [team[0][pk] for pk in player_keys]
    op_info = [op[0][pk] for pk in player_keys]
    # Parse the deck
    team_info[-1] = ';'.join(sorted([c[ck] for c in (team_info[-1]) for ck in card_keys]))
    op_info[-1] = ';'.join(sorted([c[ck] for c in (op_info[-1]) for ck in card_keys]))
    # Merge all and format as csv
    total_data = [btype, time, mode['name']]
    total_data.extend(team_info)
    total_data.extend(op_info)
    return (','.join(list(map(str,total_data))))
    


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Process ClashRoyale API player battles request')
    
    # File containing players' tags
    parser.add_argument('-p', dest = 'players', action = 'store', required = True)
    
    # File with API token
    parser.add_argument('-t', dest = 'fileToken', action = 'store', required = True)
    
    # File to add battles
    parser.add_argument('-o', dest = 'output', action = 'store', default = 'output.csv')
    
    args = parser.parse_args()
    
# Seting up API token and tags to request
with open(args.fileToken, 'r+') as tok_file:
    token = tok_file.read()

with open(args.players, 'r+') as tags_file:
    tags = tags_file.read().split(' ')

# Making the requests and storing the data
data = []
async_request(tags, token, data)

historic_data = pd.read_csv(args.output)
# Drop empty responses
data = [d for d in data if d]
new_data = pd.read_csv(io.StringIO('\n'.join(data)), names=list(historic_data))

# Combine old and new data, dropping repeated rows
pd.concat([historic_data, new_data]).drop_duplicates().to_csv(args.output, index=False)

#python.exe .\battles_mining.py -p tags.txt -t .\token.txt