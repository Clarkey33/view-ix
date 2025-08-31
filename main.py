from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from src.fpl_api_scraper import get_fpl_metadata,get_fpl_metadata_cached,get_manager_team,create_player_map
from src.fpl_api_scraper import get_fixtures, create_team_mapping, get_fixture_difficulty, create_position_mapping
from src.fpl_api_scraper import map_player_status, construct_player_image_url
from src.models import PlayerDetail, TeamDetailsResponse, Fixture
import httpx
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

@app.get("/get_team_details")
async def get_manager_team_details(team_id:int,game_week:int):

    manager_team_picks = await get_manager_team(team_id, game_week)
    bootstrap_data = await get_fpl_metadata_cached()
    fixtures_metadata = await get_fixtures()

    player_map = await create_player_map(bootstrap_data)
    team_map = await create_team_mapping(bootstrap_data)
    position_map = await create_position_mapping(bootstrap_data)

    start_certainty = None
    
    if not bootstrap_data: #or not fixtures_metadata:
        print("essential data source could not be retrieved from API")
        raise HTTPException(status_code=503, detail="Could not retrieve core data from FPL API")
      
    manager_team_details= []
    for pick in manager_team_picks:
        player_id = pick.get("element")
        player_details = player_map.get(player_id)

        if player_details:
            print(f"Accessing fixture difficulty for: {player_id}")
            fixture_difficulty_list = await get_fixture_difficulty(
                current_game_week=game_week,
                player_id=player_id,
                player_map=player_map,
                team_map=team_map,
                fixtures_metadata=fixtures_metadata
                )
            
            next_fixture = fixture_difficulty_list[0] if fixture_difficulty_list else {}
            next_opponent_name = next_fixture.get("opponent_name","N/A")
            next_opponent_difficulty = next_fixture.get('difficulty',0)
            
            team_id = player_details.get("team")
            team_name = team_map.get(team_id)
            position_id = player_details.get("element_type")
            position = position_map.get(position_id, "UNK")

            fpl_status = player_details.get("status", "u")
            player_availability = map_player_status(fpl_status)
            player_news = player_details.get("news","No news available")

            player_code=player_details.get("code",0)
            photo_url = construct_player_image_url(player_code=player_code)
            print("photo_url:", photo_url)

            number_of_starts= player_details.get('starts',0)
            start_ratio = number_of_starts/game_week if game_week > 0 else 0
            
            if player_availability == 'Unavailable' or player_availability == 'Suspended' or player_availability == 'Injured':
                start_certainty = "Bench Player"
            elif player_availability == 'Doubtful' and start_ratio >.60:
                start_certainty = "Doubtful (but a regular starter)"
            elif player_availability == 'Doubtful' and start_ratio <.60:
                start_certainty = "Doubtful (and not a regular starter)"
            elif player_availability == 'Available' and start_ratio >=.85:
                start_certainty = "High"
            elif player_availability == 'Available' and start_ratio >=.60:
                start_certainty = "Likely Starter"
            elif player_availability == 'Available' and start_ratio >=.30 and start_ratio <.60:
                start_certainty = "Rotation Risk"
            else:
                start_certainty= "Bench Player"


            combined_data ={
                **pick,
                **player_details,
                "player_status": player_availability,
                "player_news": player_news,
                "start_certainty": start_certainty,
                "team_name": team_name,
                "position": position,
                "next_opponent_name": next_opponent_name,
                "next_opponent_difficulty": next_opponent_difficulty,
                "photo_url":photo_url

            }
            
            player_obj = PlayerDetail(**combined_data)
            manager_team_details.append(player_obj)

    print(f"Successfully retrieved details for manager's team of {len(manager_team_details)} players.")
    return TeamDetailsResponse(players=manager_team_details)











    


