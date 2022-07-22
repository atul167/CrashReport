import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

#Our data is stored in the following location.
DATA_URL = (r"Crashes.csv")
#heading
st.title("Motor Vehicle Collisions in New York City")
st.markdown("Made by Atul Dwivedi")
st.markdown("This app displays and analyzes motor vehicle collisions in New York City")

@st.cache(persist=True)#as we are cd cdperforming dropna and rename on 
#thousands of columns , the gpu cycles can add up very fast
#it makes the process more efficient as it prevents recalling of all functions when the site is reloaded
def load_data(nrows):#function to load data
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])#here we parse the dates and convert it to pandas date time format.
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)#dropping the NA values 
    lowercase = lambda x: str(x).lower()#lowering the case of each of the column names by using .lower function
    data.rename(lowercase, axis="columns", inplace=True)#renaming the columns with lowercase function
    data.rename(columns={"crash_date_crash_time": "date/time"}, inplace=True)#renaming the column name as date/time
    return data

data = load_data(100000)#loading 100000 rows of data

st.header("Which location has the most number of injured people in NYC?")
injured= st.slider("Number of persons injured in vehicle collisions", 0, 19)#range is 0 to 19 as the maximum number of people injured was 19 in the dataset at a given spot
st.map(data.query("injured_persons >= @injured")[["latitude", "longitude"]].dropna(how="any"))

#using query function to filter data ,here we are checking if column value exceeds the slider variable i.e injured 
#we return two values i.e. latitude and longitude so that we can plot in on a map
#drop the NA values , such that if anyone of them is NA, the row will be dropped

st.header("Collisons occurence during a given time of day")
hour = st.slider("Hour to look at", 0, 23)#slider to select hour of the day
original_data = data #Copying data to origianal_data
data = data[data['date/time'].dt.hour == hour]#Subsetting the data

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))#Vehicle collisions between hour and hour+1
midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))#taking average of latitude values and longitude 
#intial coodinate for the intial view state have been defined
st.write(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 12,
        "pitch": 50,#3d plot
    },
    #specifying layers in a list
    layers=[
        #using a tuple 
        pdk.Layer(
        "HexagonLayer",
        data=data[['date/time', 'latitude', 'longitude']],#subsetting the data by 3 columns
        get_position=["longitude", "latitude"],#getting the position from latitude and longitude columns
        auto_highlight=True,
        radius=75,#radius of each point in the data 
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0, 1000],
        ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]
#creating a histogram
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)#chart data where x axis is given by minute and y axis by crashes
st.write(fig)#passing figure to st.write

st.header("Top 10 dangerous streets by affected class")
select = st.selectbox('Affected class', ['Pedestrians', 'Cyclists', 'Motorists'])
#creating a dropdown list so that we can select either of Pedestrians,Cyclists,Motorists.
if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how="any")[:10])
#if injury number is greater than 1 there has been an injury 
#here we are only selecting the top 10 values
elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how="any")[:10])

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how="any")[:10])


if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)
