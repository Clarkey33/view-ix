import httpx
import time
import json
from config import BASE_URL, CACHE_DURATION_SECONDS,LAST_CACHE_TIME

cached_bootstrap_data= None

async def get_fpl_metadata(base_url:str=BASE_URL)-> dict:
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

    global cached_bootstrap_data, LAST_CACHE_TIME
    current_time= time.time()

    if not cached_bootstrap_data or (current_time-LAST_CACHE_TIME > CACHE_DURATION_SECONDS):
        print("CACHE Expired: Fetching new bootstrap data from FPL API")
        cached_bootstrap_data = await get_fpl_metadata()
        LAST_CACHE_TIME=current_time
    else:
        print("Using existing bootstrap data.")
    return cached_bootstrap_data


async def create_team_mapping(bootstrap_data:dict)->dict:
    team_list = bootstrap_data.get('teams',[])
    team_map = {team["id"]: team['name'] for team in team_list}

    return team_map

async def get_manager_team(
        team_id:int, 
        game_week:int,
        base_url:str=BASE_URL
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
    

async def get_fixtures(base_url:str=BASE_URL):
    url = f"{base_url}/fixtures/"
    try:
        async with httpx.AsyncClient() as client:
            print("Acessing fixtures lists")
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error retrieving fixtures: {e}")
        return None
    
async def get_fixture_difficulty(
        current_game_week:int,
        player_id:int,
        player_map:dict,
        #team_map:dict,
        fixtures_metadata:list
        ) -> list:
   
   player_info= player_map.get(player_id)
   if not player_info or not fixtures_metadata:
       print("could not retrieve essential data sources")
       return []
   
   player_team_id = player_info.get("team")
   next_three_fixtures= [current_game_week+1, current_game_week+2, current_game_week+3]
   fixture_difficulty=[]

   for match in fixtures_metadata:
       game_week=match.get("event")

       if game_week in next_three_fixtures:
           away_team = match.get('team_a')
           home_team = match.get('team_h')

           if away_team==player_team_id:
               difficulty=match.get('team_a_difficulty')
               fixture_difficulty.append(difficulty)
           elif home_team==player_team_id:
               difficulty=match.get('team_h_difficulty')
               fixture_difficulty.append(difficulty)

   return fixture_difficulty
               
                        
               



           






    












