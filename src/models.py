from pydantic import BaseModel, Field
from typing import List, Optional


class PlayerDetail(BaseModel):

    element:int = Field(..., description="The player's unique FPL ID")
    is_captain:bool
    is_vice_captain:bool

    code:int
    photo_url:str = Field(..., description="The full url for player image")
    web_name:str= Field(..., description="The name of player's club")
    now_cost:int= Field(...,description="The player's current price x 10")
    position:str= Field(..., description="The player's position(GKP, DEF, MID, FWD)")
    team_name:str= Field(..., description="The name of the player's club")
    event_points:int= Field(..., description="The player's points for current gameweek")
    minutes:Optional[int]
    points_per_game:Optional[float]

    player_status:str = Field(..., description=" Dashboard feature for player availability example: 'Available', 'Doubtful', 'Injured'")
    player_news:str = Field(..., description="The latest news on player, example injury news")
    start_certainty:str = Field(..., description="User defined metric for how certain a player is of starting next gameweek")

    next_opponent_name:str = Field(..., description="Club name of nex fixture opponent")
    next_opponent_difficulty:int = Field(..., description="Rating of fixture difficulty from 1-5")

    class Config:
        from_attributes = True

class TeamDetailsResponse(BaseModel):

    players: List[PlayerDetail]


class Fixture(BaseModel):
    opponent_name:str
    difficulty:int
    is_home:bool
