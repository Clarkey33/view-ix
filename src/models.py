from pydantic import BaseModel, Field
from typing import List, Optional


class PlayerDetail(BaseModel):

    element:int = Field(..., description="The player's unique FPL ID")
    is_captain:bool
    is_vice_captain:bool

    code:int
    photo_url:str= Field(..., description="The full url for player image")
    web_name:str= Field(..., description="The name of player's club")
    now_cost:Optional[int]= Field(default=None,description="The player's current price x 10")
    position:str= Field(..., description="The player's position(GKP, DEF, MID, FWD)")
    team_name:str= Field(..., description="The name of the player's club")
    event_points:Optional[int]= Field(default=None, description="The player's points for current gameweek")
    minutes:Optional[int]
    points_per_game:Optional[float]
    defensive_contribution_per_90:Optional[float] = Field(default=None, description="Average count of player's defensive actions")
    defensive_contribution:Optional[float] = Field(default=None, description="A count of players defensive actions")

    player_status:Optional[str] = Field(default=None, description=" Dashboard feature for player availability example: 'Available', 'Doubtful', 'Injured'")
    player_news:Optional[str] = Field(default=None, description="The latest news on player, example injury news")
    start_certainty:Optional[str] = Field(default=None, description="User defined metric for how certain a player is of starting next gameweek")

    next_opponent_name:Optional[str] = Field(default=None, description="Club name of next fixture opponent")
    next_opponent_difficulty:Optional[int] = Field(default=None, description="Rating of fixture difficulty from 1-5")
    goals_scored: int
    assists: int

    opponent: Optional[str] = Field(None, description="Opponent for a past gameweek")
    player_team_score: Optional[int] = Field(None)
    opponent_team_score: Optional[int] = Field(None)
    bps:Optional[int]= Field(default=None, description="Bonus player System")



    class Config:
        from_attributes = True

class TeamDetailsResponse(BaseModel):
    players: List[PlayerDetail]


class Fixture(BaseModel):
    opponent_name:str
    difficulty:int
    is_home:bool


class PlanningPlayerDetail(BaseModel):

    element:int= Field(..., description="The player's unique FPL ID")
    position:str= Field(..., description="The player's position(GKP, DEF, MID, FWD)")
    is_captain:bool
    is_vice_captain:bool

    first_name:str
    second_name:str
    web_name:str= Field(..., description="The name of player's club")

    player_status:str= Field(..., description=" Dashboard feature for player availability example: 'Available', 'Doubtful', 'Injured'")
    now_cost:int= Field(...,description="The player's current price x 10")
    player_news:str= Field(..., description="The latest news on player, example injury news")
    team_name:str= Field(..., description="The name of the player's club")
    photo_url:str= Field(..., description="The full url for player image")
    next_3_fixtures: list= Field(..., description="list of next 3 fixtures")
    defensive_contribution_per_90:Optional[float] = Field(default=None, description="Average count of player's defensive actions")
    goals_scored: int
    assists: int


class PlanningViewResponse(BaseModel):
    view_mode: str = "planning"
    requested_gameweek:int
    roster_gameweek: int
    players: list[PlanningPlayerDetail]