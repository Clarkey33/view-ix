import httpx

base_url = 'https://fantasy.premierleague.com/api' 
async def create_team_mapping(bootstrap_data:dict)->dict:
    team_list = bootstrap_data.get('teams',[])
    team_map = {team["id"]: team['name'] for team in team_list}

    return team_map


async def get_fixture_difficulty(base_url:str = base_url):

    try:
        async with httpx.AsyncClient() as client:
            print("Acessing fixtures lists")









