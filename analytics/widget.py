import sys
import os
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0,root)

import asyncio
import aiohttp
import streamlit as st
from src.extract import fetch_city
from src.weather_dict import WEATHER_MAPPING
import pandas as pd
from unidecode import unidecode

st.set_page_config(page_title="Weatherly",page_icon="🌤",layout="centered")
st.title("Weatherly",text_alignment="center")
city_input = st.text_input("Search City Name")
df = pd.read_csv("data/in.csv")
cities = {
    unidecode(city).strip().lower(): (lat, lon)
    for city, lat, lon in zip(df["city"], df["lat"], df["lng"])
}
city_mod = unidecode(city_input).strip().lower()

async def weather_widget_setup():
    sem = asyncio.Semaphore(1)
    time = aiohttp.ClientTimeout(total=12)
    async with aiohttp.ClientSession(timeout=time) as session:
        return await fetch_city(
            session=session,
            semaphore=sem,
            city=city_input,
            lat=lat,
            lon=lon
        )

if st.button("Get Weather"):
    cor = cities.get(city_mod)
    if cor:
        lat, lon = cor
        with st.spinner("Fetching Weather.."):
            w = asyncio.run(weather_widget_setup())
            info = w["data"]["current"]
            visibility = info["visibility"]/1000
            condition = WEATHER_MAPPING.get(info["weather_code"],"Unknown")
            with st.container():
                st.subheader(f"City : {city_input}")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Temperature",f"{info["temperature_2m"]}°C")
                with col2:
                    st.metric("Humidity",f"{info["relative_humidity_2m"]} %")
                with col3:
                    st.metric("Wind Speed",f"{info["wind_speed_10m"]}km/h")
                with col4:
                    st.metric("Visibility",f"{visibility:.2f} km")
                
                st.metric("Weather Conditions", f"{condition}")
                
                st.caption(f"Last Updated : {w["extraction_time"]}")

with st.sidebar:
    st.write("Made by Shataghnee")

                
                    
                



    
    
