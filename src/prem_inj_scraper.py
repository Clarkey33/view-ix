import httpx
from bs4 import BeautifulSoup
from config import BASE_URL_INJ

async def get_html(url:str=BASE_URL_INJ)->str:
    
    try:
        async with httpx.AsyncClient() as client:
            print("Scraping webpage..")
            response = await client.get(url, http2=True)
            response.raise_for_status()
            response_html = response.text()
            return response_html
    except Exception as e:
        print(f"Error retrieving html: {e}")
        return None
    

            
async def parse_html()->str:
    html_content = get_html()

    soup = BeautifulSoup(html_content,'html.parser')
    
    soup.find('div', class_="injury-table-full-wrap")





