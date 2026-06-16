from sqlalchemy import create_engine
import pandas as pd
import logging
import os
from dotenv import load_dotenv
load_dotenv()
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
url = f"postgresql+psycopg://{username}:{password}@{host}:{port}/weather_db"
logging.basicConfig(filename="logs/load_log.log",level=logging.INFO,format="%(asctime)s,%(levelname)s,%(message)s")
def load_data():
    try:
         df = pd.read_json("data/transformed_data.json")
    except FileNotFoundError as e:
        logging.error("File does not exist")
        return
    try:
        engine = create_engine(url,echo=True)
    except Exception as e:
        logging.error("Engine cannot be created")
        return
    logging.info("Engine creation Successful")
    try:
        df.to_sql(
        name="weather_data",
        con=engine,
        if_exists="append",
        index=False
        )
    except Exception as e:
        logging.exception(f"Faild to load data : {e}")
        return
    logging.info("File Successfully loaded to SQL")
    
if __name__ == "__main__":
    load_data()