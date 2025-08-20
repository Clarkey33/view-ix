from fastapi import FastAPI
import httpx
import json
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


@app.get("/get-team-data")
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

@app.get("/get-player-data")
async def show_manager_team(
    team_id:int, 
    game_week:int,
    base_url:str=base_url):

    managers_team = await get_manager_team(team_id,game_week, base_url)

    # url = f"{base_url}/bootstrap-static/"
    # try:
    #     async with httpx.AsyncClient() as client:
    #         print(f"Attempting to access Total Players API..")
    #         response = await client.get(url)
    #         response_json = response.json()
    #         total_players_list = response_json.get("elements")
    #         #print(total_players_list)
    #         if total_players_list:
    #             print(f"Total Players Meta data retrieved succesfully")
    #             return total_players_list
        
    # except httpx.HTTPError as exc:
    #     print(f"HTTP Exception for {exc.request.url} - {exc}")
    # except Exception as e:
    #     return f"Error occured during retrieval: {e}"




    


