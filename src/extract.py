import pandas as pd
import json
from datetime import datetime
import logging
import asyncio 
import aiohttp
import os
from dotenv import load_dotenv
load_dotenv()
url = os.getenv("API_URL")
concurrent_users = int(os.getenv("MAX_CON_FETCH"))
logging.basicConfig(filename="logs/extract_logs.log",level=logging.INFO,format="%(asctime)s,%(levelname)s,%(message)s")
TIMEOUT = 10
combined_raw_data = []
async def fetch_city(session,semaphore,city,lat,lon):
    params ={
        "latitude" : lat,
        "longitude" : lon,
        "current" : "temperature_2m,wind_speed_10m,relative_humidity_2m,visibility,weather_code"
        }
    try:
        async with semaphore:
            async with session.get(url,params=params) as resp:
                logging.info(resp.raise_for_status)
                raw_data = {
                    "city" : city,
                    "latitude" : lat,
                    "longitude" : lon,
                    "data" : await resp.json(),
                    "extraction_time" : datetime.now().time().isoformat()
                }
                logging.info(f"Successful Extraction of weather data for {city}")
    except aiohttp.ClientResponseError as e:
        logging.exception(f"API failed for {city}: {e}")
        return
    except aiohttp.ClientError as e:
        logging.exception(f"Failed to fetch data for {city} : {e}")
        return        
    return raw_data    
             
    
async def extract_data():
    try:
        extract_df = pd.read_csv("data/in.csv",delimiter=",")
        extract_df.set_index("city",inplace=True)
    except FileNotFoundError as e:
        logging.error("CSV File does not exist")
        return
    cities = dict(zip(extract_df.index,zip(extract_df["lat"],extract_df["lng"])))
    sem = asyncio.Semaphore(concurrent_users)
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            fetch = [
                fetch_city(session=session,semaphore=sem,city=city,lat=lat,lon=lon)
                for city,(lat,lon) in cities.items()
            ]
            res = await asyncio.gather(*fetch,return_exceptions=True)
            for result in res:
                if result is not None:
                    combined_raw_data.append(result)
            with open("data/raw_data.json","w") as f:
                json.dump(combined_raw_data,f,indent=2)
                            
    except Exception as e:
        logging.exception("Data cannot be converted to JSON")
    logging.info("Data Successfully Ingested")
    
if __name__ == "__main__":
    asyncio.run(extract_data())       
    
    
        
        
    
        