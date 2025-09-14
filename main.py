from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from src.fpl_api_scraper import get_fpl_metadata,get_fpl_metadata_cached,get_manager_team,create_player_map
from src.fpl_api_scraper import get_fixtures, create_team_mapping, get_fixture_difficulty, create_position_mapping
from src.fpl_api_scraper import map_player_status, construct_player_image_url
from src.models import PlayerDetail, TeamDetailsResponse, Fixture, PlanningPlayerDetail, PlanningViewResponse
import httpx
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

#origins = ["*"]
origins = [
    "https://view-ix.vercel.app",
    "http://127.0.0.1:8001",
    "http://localhost:8001",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

@app.get("/get_team_details")
async def get_manager_team_details(team_id:int,game_week:int):

    gameweek_status= await get_gameweek_status()
    current_gameweek = gameweek_status.get("current_gameweek")
    
    bootstrap_data = await get_fpl_metadata_cached()
    fixtures_metadata = await get_fixtures()

    player_map = await create_player_map(bootstrap_data)
    team_map = await create_team_mapping(bootstrap_data)
    position_map = await create_position_mapping(bootstrap_data)

    start_certainty = None

    if not bootstrap_data: 
        print("essential data source could not be retrieved from API")
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve core data from FPL API"
            )
        
    
    is_planning_view = game_week > current_gameweek
    # is_live_view = game_week == current_gameweek
    # is_historical_view = game_week < current_gameweek
    roster_gameweek = current_gameweek if is_planning_view else game_week

    manager_team_picks = await get_manager_team(team_id, roster_gameweek)

    manager_team_details= []

    for pick in manager_team_picks:
        player_id = pick.get("element")
        player_details = player_map.get(player_id)

        if not player_details:
                continue
        
        base_player_data = {
            **pick,
            **player_details,
            "team_name":team_map.get(player_details.get("team")),
            "position": position_map.get(player_details.get("element_type")),
            "photo_url":construct_player_image_url(player_code=player_details.get("code",0))

        }
               

        if is_planning_view:
            fixture_difficulty_list = await get_fixture_difficulty(
                current_game_week=game_week,
                player_id=player_id,
                player_map=player_map,
                team_map=team_map,
                fixtures_metadata=fixtures_metadata
            )

            player_obj = PlanningPlayerDetail(
                **base_player_data,
                player_availability= map_player_status(player_details.get("status", "u")),
                player_news = player_details.get("news","No news available"),
                next_3_fixtures=fixture_difficulty_list
            )
        else:
            player_obj_data = {**base_player_data}

            if game_week == current_gameweek:
                player_availability = map_player_status(player_details.get("status", "u"))
                player_obj_data["player_status"]= player_availability

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

                player_obj_data["start_certainty"] = start_certainty
                player_obj_data["event_points"] = player_details.get("event_points", 0)
                player_obj_data["bps"] = player_details.get("bps", 0)
                player_obj_data["defensive_contribution_per_90"] = player_details.get(
                    "defensive_contribution_per_90", 0.0
                    )
            else:
                fixture_list = await get_fixture_difficulty(game_week,
                                                            player_id, 
                                                            player_map, 
                                                            team_map,
                                                            fixtures_metadata
                                                            )
                
                player_obj_data = {**base_player_data}

                if fixture_list:
                    historical_fixture = fixture_list[0]
                    player_obj_data["opponent"] = historical_fixture.get("opponent_name")
                    player_obj_data["player_team_score"] = historical_fixture.get("player_team_score")
                    player_obj_data["opponent_team_score"] = historical_fixture.get("opponent_team_score")

            player_obj = PlayerDetail(**player_obj_data)
            manager_team_details.append(player_obj)

    if is_planning_view:
        return PlanningViewResponse(
            requested_gameweek=game_week,
            roster_gameweek=current_gameweek,
            players= manager_team_details
        )
    else:
        return TeamDetailsResponse(players=manager_team_details)
                
                    

@app.get("/gameweek_status")
async def get_gameweek_status()->dict:

    fpl_metadata = await get_fpl_metadata_cached()

    if not fpl_metadata:
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve core metadata from the FPL API. It may be temporarily down."
        )


    events_list = fpl_metadata.get('events',[])

    gameweek_num=None
    status={}

    for event in events_list:
        print(f"Attempting to retrieve current gameweek")
        current_status = event.get("is_current")
        try:

            if current_status == True:
                gameweek_num = int(event.get('id'))
                print(f"Current game week found")
                status['current_gameweek']= gameweek_num
                status['previous_gameweek'] = gameweek_num -1
                status['next_gameweek'] = gameweek_num +1
                return status
            else:
                continue
        except Exception as e:
            print(f"Failed to find current gameweek {e}")
            return {}
        
