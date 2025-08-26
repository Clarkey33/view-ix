from fastapi import FastAPI
from src.fpl_api_scraper import get_fpl_metadata,get_fpl_metadata_cached,get_manager_team,create_player_map
from src.fpl_api_scraper import get_fixtures, create_team_mapping, get_fixture_difficulty
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
    team_mapping = await create_team_mapping(bootstrap_data)

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
    
    if not fixtures_metadata:
        print("league fixtures not extracted")
        return None
    
    print("fixture_metadata:",len(fixtures_metadata), type(fixtures_metadata))

    if not team_mapping:
        print("Team map not created")
        return None
    
    for pick in manager_team_picks:
        player_id = pick.get("element")
        player_details = player_map.get(player_id)
        fixture_difficulty = await get_fixture_difficulty(
            game_week=game_week,
            player_map=player_map,
            team_map=team_mapping,
            fixtures_metadata= fixtures_metadata 
        )
        if player_details:
            combined_data = pick | player_details | fixture_difficulty
            manager_team_details.append(combined_data)

    print(f"Successfully retrieved details for manager's team of {len(manager_team_details)} players.")
    return manager_team_details







    


