from fastapi import FastAPI
import httpx

app = FastAPI()

base_url= 'https://fantasy.premierleague.com/api' 

@app.get("/")
async def read_root():
    return "Hello from view-xi!"

@app.get("/get-team-data")
async def get_manager_team(
        team_id:int, 
        game_week:int,
        base_url:str=base_url
        ):

    url = f"{base_url}/entry/{team_id}/event/{game_week}/picks/"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

            print("Status Code:", response.status_code)
            print("Response Text:", response.text)

    except httpx.HTTPError as exc:
        print(f"HTTP Exception for {exc.request.url} - {exc}")
    except Exception as e:
        return f"Error occured during retrieval: {e}"

    return response.json()



    #get fpl managers current list of players
    #get respective players metadata
    #send this raw JSON data to an api that will display


