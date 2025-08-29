import httpx
from bs4 import BeautifulSoup
from config import BASE_URL_INJ
from io import StringIO
import random
import pandas as pd
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


async def get_html(url:str=BASE_URL_INJ)-> str:

    CHROME_EXECUTABLE_PATH ="/usr/bin/google-chrome"
   
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = None
    try:
        print("Launching stealth browser...")
        driver = uc.Chrome(browser_executable_path=CHROME_EXECUTABLE_PATH, options=options)
        
        print(f"Navigating to {url}...")
        driver.get(url)
        
       
        print("Waiting for Cloudflare verification (20 seconds)...")
        time.sleep(20)
     
        
        print("Extracting final page content...")
        html_content = driver.page_source
        
        if "Verifying you are human" in html_content or "review the security of your connection" in html_content:
            print("!!! FAILED: Could not bypass Cloudflare verification after waiting.")
            print("Saving final screenshot to 'cloudflare_failure.png'...")
            driver.save_screenshot("cloudflare_failure.png")
            return None
        
        print("SUCCESS: Bypassed Cloudflare. Now parsing content.")
        return html_content

    except Exception as e:
        print(f"An error occurred with undetected-chromedriver: {e}")
        return None
    finally:
        if driver:
            driver.quit()
            print("Browser closed.") 
            

async def parse_html(html_content:str)->str:

    if not html_content:
        print("Error: html content not found")
        return None

    try:
        soup = BeautifulSoup(html_content,'html.parser')
        #div_with_table=soup.find('div', class_="injury-table-full-wrap")
        table = soup.find('table', class_="injury-table-full")
        #print(table)
        if not table:
            print("Could not find the injury table on the page")
            return None
    except Exception as e:
        print(f'Could not retrieve table: {e}')
    return StringIO(str(table))


async def create_clean_dataframe(table:str)-> dict:

    if table:
        print('Creating and cleaning player injury dataframe')
        df = pd.read_html(str(table))[0]
        df = df[['Player','Reason','Status']]
        df=df.fillna('n/a')


        df.set_index('Player',inplace=True)
        injury_dict = df.to_dict(orient='index')

        print('Player Injury mapping succesfully created')
        return injury_dict


async def get_player_injury_status()->dict:

    html_content = await get_html()
    table = await parse_html(html_content=html_content)
    player_injury_map = await create_clean_dataframe(table=table)

    return player_injury_map












