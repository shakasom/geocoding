import time 
import base64

import streamlit as st
import pandas as pd 
import geopandas as gpd 

import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

import matplotlib.pyplot as plt
import plotly_express as px 

st.title("Geocoding Application in Python")
st.markdown("Uppload a CSV File with address columns (Street name & number, Postcode, City)")



def create_address_col(df):
    st.sidebar.title("Select Address columns")
    st.sidebar.info("You need to select address column (Street name and number), post code and City")
    address_name = st.sidebar.selectbox("Select Address column", df.columns.tolist())
    post_code = st.sidebar.selectbox("Select Post Code Column", df.columns.tolist())
    city = st.sidebar.selectbox("Select the City Column", df.columns.tolist())
    country = st.sidebar.text_input("Write the country of the addresses")
    

    df["geocode_col"] =  df[address_name].astype(str) + ',' + \
                df[post_code] + ',' + \
                df[city] + ',' + \
                country   
    return df
    
def choose_geocode_column(df):
    selection = st.selectbox("Select the column", df.columns.tolist())
    df["geocde_col"] = df[selection]
    return df

def geocode(df):
    locator = Nominatim(user_agent="myGeocoder")
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1)
    df['location'] = df['geocode_col'].apply(geocode)
    df['point'] = df['location'].apply(lambda loc: tuple(loc.point) if loc else None)

    df[['latitude', 'longitude', 'altitude']] = pd.DataFrame(df['point'].tolist(), index=df.index)
    return df 

@st.cache(persist=True, suppress_st_warning=True)
def display_map(df):
    px.set_mapbox_access_token("pk.eyJ1Ijoic2hha2Fzb20iLCJhIjoiY2plMWg1NGFpMXZ5NjJxbjhlM2ttN3AwbiJ9.RtGYHmreKiyBfHuElgYq_w")
    fig = px.scatter_mapbox(df, lat='latitude', lon='longitude', zoom=10)
    return fig

def download_csv(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (right-click and save as &lt;some_name&gt;.csv)'
    return href


def main():
    file = st.file_uploader("Choose a file")
    if file is not None:
        file.seek(0)
        df = pd.read_csv(file, low_memory=False)
        with st.spinner('Reading CSV File...'):
            time.sleep(5)
            st.success('Done!')
        st.write(df.head())
        st.write(df.shape)



        cols = df.columns.tolist()

        st.subheader("Choose Address Columns from the Sidebar")
        st.info("Example correct address: Karlaplan 13,115 20,STOCKHOLM, Sweden")
    
    if st.checkbox("Address Formatted correctly (Example Above)"):
        df_address = choose_geocode_column(df)
        st.write("choosing columns...")
        st.write(df_address["geocode_col"].head())
        st.write("Starting to Geocode")
        geocoded_df = geocode(df_address)
        with st.spinner('Geocoding Hold tight...'):
            time.sleep(5)
        st.success('Done!')
        st.write(geocoded_df.head())
        st.plotly_chart(display_map(geocoded_df))
            
        st.markdown(download_csv(geocoded_df), unsafe_allow_html=True)
    
    if st.checkbox("Not Correctly Formatted"):
            df_address = create_address_col(df)
            st.write(df_address["geocode_col"])
            geocoded_df = geocode(df_address)
            with st.spinner('Geocoding Hold tight...'):
                time.sleep(5)
            st.success('Done!')
            st.plotly_chart(display_map(geocoded_df))
            st.markdown(download_csv(geocoded_df), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
