from fastapi import FastAPI, HTTPException
from src.fpl_api_scraper import get_fpl_metadata,get_fpl_metadata_cached,get_manager_team,create_player_map
from src.fpl_api_scraper import get_fixtures, create_team_mapping, get_fixture_difficulty
from src.prem_inj_scraper import get_player_injury_status
import httpx
#import json
#import time

app = FastAPI()

@app.get("/")
async def read_root():
    return "Hello from view-xi!"

@app.get("/get_team_details")
async def get_manager_team_details(team_id:int,game_week:int):

    manager_team_picks = await get_manager_team(team_id, game_week)
    bootstrap_data = await get_fpl_metadata_cached()
    player_map = await create_player_map(bootstrap_data)
    fixtures_metadata = await get_fixtures()
    injury_map = await get_player_injury_status()
    
    if not manager_team_picks or not bootstrap_data or not fixtures_metadata:
        print("One or more essential data sources could not be retrieved from API")
        raise HTTPException(status_code=503, detail="Could not retrieve all data from FPL API")
      
    manager_team_details= []
    for pick in manager_team_picks:
        player_id = pick.get("element")
        player_details = player_map.get(player_id)

        if player_details:
            print(f"Accessing fixture difficulty for: {player_id}")
            fixture_difficulty = await get_fixture_difficulty(
                current_game_week=game_week,
                player_id=player_id,
                player_map=player_map,
                fixtures_metadata=fixtures_metadata
                )
            
            player_name = player_details.get("web_name")
            fitness_status = injury_map.get(player_name,"Fit")

            combined_data = pick | player_details | {"future_fixtures":fixture_difficulty} | {"fitness_status": fitness_status}
            manager_team_details.append(combined_data)

    print(f"Successfully retrieved details for manager's team of {len(manager_team_details)} players.")
    return manager_team_details







    


