from fastapi import FastAPI
import httpx
#import json
import time

app = FastAPI()

base_url= 'https://fantasy.premierleague.com/api' 

cached_bootstrap_data= None
last_cache_time=0
CACHE_DURATION_SECONDS = 3600

@app.get("/")
async def read_root():
    return "Hello from view-xi!"


async def get_fpl_metadata(base_url:str=base_url)-> dict:
    url = f"{base_url}/bootstrap-static/"
    try:
        async with httpx.AsyncClient() as client:
            print(f"Attempting to access Total Players API..")
            response = await client.get(url)
            return response.json()
            
    except httpx.HTTPError as exc:
        print(f"HTTP Exception for {exc.request.url} - {exc}")
    except Exception as e:
        return f"Error occured during retrieval: {e}"
    
async def create_player_map(bootstrap_data:dict)-> dict:

    player_list = bootstrap_data.get("elements",[])
    player_map = {player["id"]: player for player in player_list}

    return player_map

async def get_fpl_metadata_cached() -> dict:

    global cached_bootstrap_data, last_cache_time
    current_time= time.time()

    if not cached_bootstrap_data or (current_time-last_cache_time > CACHE_DURATION_SECONDS):
        print("CACHE Expired: Fetching new bootstrap data from FPL API")
        cached_bootstrap_data = await get_fpl_metadata()
        last_cache_time=current_time
    else:
        print("Using existing bootstrap data.")
    return cached_bootstrap_data

#@app.get("/get-team-data")
async def get_manager_team(
        team_id:int, 
        game_week:int,
        base_url:str=base_url
        ) -> list:

    url = f"{base_url}/entry/{team_id}/event/{game_week}/picks/"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response_json = response.json()
            managers_team = response_json.get("picks")
            print(f"Manager's picks retrieved succesfully")
            #print(f" data type: {type(managers_team)}")
            return managers_team
    except httpx.HTTPError as exc:
        print(f"HTTP Exception for {exc.request.url} - {exc}")
    except Exception as e:
        return f"Error occured during retrieval: {e}"


@app.get("/get_team_details")
async def get_manager_team_details(team_id:int,game_week:int):
    manager_team_picks = await get_manager_team(team_id, game_week)
    bootstrap_data = await get_fpl_metadata_cached()
    player_map = await create_player_map(bootstrap_data)

    manager_team_details= []
    if not manager_team_picks:
        print("manager team picks not extracted")
        return None
    
    if not bootstrap_data:
        print("bootstrap data not extracted")
        return None
    
    if not player_map:
        print("Player map not created")
        return None
    
    for pick in manager_team_picks:
        player_id = pick.get("element")
        player_details = player_map.get(player_id)

        if player_details:
            combined_data = pick | player_details
            manager_team_details.append(combined_data)

    print(f"Successfully retrieved details for manager's team of {len(manager_team_details)} players.")
    return manager_team_details







    


