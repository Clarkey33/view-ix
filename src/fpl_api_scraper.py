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
        print(f"Error occured during retrieval: {e}")
        return None
    
async def create_player_map(bootstrap_data:dict)-> dict:

    player_list = bootstrap_data.get("elements",[])
    player_map = {player["id"]: player for player in player_list}

    return player_map

async def get_fpl_metadata_cached() -> dict:

    global cached_bootstrap_data, LAST_CACHE_TIME, CACHE_DURATION_SECONDS
    current_time= time.time()

    if not cached_bootstrap_data or (current_time-LAST_CACHE_TIME > CACHE_DURATION_SECONDS):
        print("CACHE Expired: Fetching new bootstrap data from FPL API")
        cached_bootstrap_data = await get_fpl_metadata()
        LAST_CACHE_TIME=current_time
        print("bootstrap data cached succesfully; available for use")
    else:
        print("Using existing bootstrap data.")
    return cached_bootstrap_data


async def create_team_mapping(bootstrap_data:dict)->dict:
    team_list = bootstrap_data.get('teams',[])
    team_map = {team["id"]: team['name'] for team in team_list}

    return team_map

async def create_position_mapping(bootstrap_data:dict)->dict:
    position_list = bootstrap_data.get("element_types",[])
    position_map = {position['id']: position['singular_name_short'] for position in position_list}
    return position_map

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
            managers_team = response_json.get("picks",[])
            print(f"Manager's picks retrieved succesfully")
            if managers_team:
                print(f"Manager's picks retrieved succesfully for GW{game_week}")
            else:
                print(f"Warning: No manager picks found for GW{game_week}. The gameweek may not have started.")
            
            return managers_team
    
    except Exception as e:
        print(f"Error retrieving manager team for GW{game_week}: {e}")
        return [] 
    

async def get_fixtures(base_url:str=BASE_URL):
    url = f"{base_url}/fixtures/"
    try:
        async with httpx.AsyncClient() as client:
            print("Acessing fixtures lists")
            response = await client.get(url)
            response.raise_for_status()
            print("fixtures list successfully retrieved")
            return response.json()
    except Exception as e:
        print(f"Error retrieving fixtures: {e}")
        return []
    
async def get_fixture_difficulty(
        current_game_week:int,
        player_id:int,
        player_map:dict,
        team_map:dict,
        fixtures_metadata:list,
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
           away_team_id = match.get('team_a')
           home_team_id = match.get('team_h')

           if away_team_id==player_team_id:
               difficulty=match.get('team_h_difficulty')
               opponent_name=team_map.get(home_team_id)
               is_home_game= False
               fixture_difficulty.append({
                   "opponent_name": f"{opponent_name} (A)",
                   "difficulty": difficulty,
                   "is_home": is_home_game,
                   "gameweek":game_week
                   })
           elif home_team_id==player_team_id:
               difficulty=match.get('team_a_difficulty')
               opponent_name=team_map.get(away_team_id)
               is_home_game= True
               fixture_difficulty.append({
                   "opponent_name": f"{opponent_name} (H)",
                   "difficulty": difficulty,
                   "is_home": is_home_game,
                   "gameweek":game_week
                   })

   return fixture_difficulty


def map_player_status(status_char:str)->str:

    if status_char == 'a':
        return "Available"
    elif status_char == 'd':
        return "Doubtful"
    elif status_char == 'i':
        return "Injured"
    elif status_char == 's':
        return "Suspended"
    else:
        return "Unavailable"
    


def construct_player_image_url(player_code:int,
                               size:str="110x140") -> str:
    
    base_url = "https://resources.premierleague.com/premierleague/photos/players/"
    return f"{base_url}{size}/p{player_code}.png"



    


 
    
    


               
                        
               



           






    












