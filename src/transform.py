import pandas as pd
from datetime import datetime
import logging
from src.weather_dict import WEATHER_MAPPING
logging.basicConfig(filename="logs/trans_log.log",level=logging.INFO,format="%(asctime)s,%(levelname)s,%(message)s")
def data_cleaning(df):
    clean_df = df.copy()
    clean_df = clean_df.rename(columns={"timezone_abbreviation":"Timezone","elevation":"Elevation",
                          "current.temperature_2m":"Temperature","current.wind_speed_10m":"Windspeed","current.relative_humidity_2m":"Humidity",
                          "current.visibility":"Visibility"})
    clean_df["Weather_Conditions"] = clean_df["current.weather_code"].map(WEATHER_MAPPING).fillna("Unknown")
    clean_df["Date"] = pd.to_datetime(df["extraction_time"]).dt.strftime("%Y-%m-%d")
    clean_df["Time"] = pd.to_datetime(df["extraction_time"]).dt.strftime("%H-%M")
    clean_df.drop(columns=["extraction_time","current.weather_code"],inplace=True)
    clean_df["Visibility"] = clean_df["Visibility"]/1000
    clean_df = clean_df.drop_duplicates()
    return clean_df
def transform_data():
    file_path = "data/raw_data.json"
    list_path = "data/drop.txt"
    try:
        df = pd.read_json(file_path)
        with open(list_path,"r") as f:
            drop_list = f.read().split(",")
    except FileNotFoundError as e:
        logging.error(f"Correct File not Found")
        return
    except ValueError as e:
        logging.error(f"Invalid JSON : {e}")
        return
    logging.info("Extraction of Raw Data Successful")
    ex1 = pd.json_normalize(df["data"])
    ex1.drop(columns=["latitude","longitude"],inplace=True,errors="ignore")
    df = pd.concat([df,ex1],axis=1)
    df.drop(columns=drop_list,inplace=True,errors='ignore')
    clean_df = data_cleaning(df)
    logging.info("Data Transformation Successful")
    clean_df.to_json("data/transformed_data.json",orient="records",indent=2)
    logging.info("Data converted to JSON for loading")
if __name__ == "__main__":
    transform_data()