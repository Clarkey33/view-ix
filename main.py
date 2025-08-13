from fastapi import FastAPI


app = FastAPI()

base_url= 'https://fantasy.premierleague.com/api' 

@app.get("/")
async def read_root():
    return "Hello from view-xi!"

@app.get("/get-team-data")
async def get_manager_team(
        team_id:str, 
        game_week:str,
        base_url:str=base_url
        ):

    url = f"{base_url}/entry/{team_id}/event/{game_week}/picks/"
    manager_page = requests.get(url)

    #get fpl managers current list of players
    #get respective players metadata
    #send this raw JSON data to an api that will display


