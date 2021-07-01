'''
Name: Duy Duong
CS230: Section SN2F
New York City Vehicle Collisions, 2015-present
URL:
'''
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk

# function to remove empty cells in the dataset
def remove_empty(column, df):
    df[column].replace('', np.nan, inplace=True)
    df.dropna(subset=[column], inplace=True)

# function to filter the dataframe to a dataframe that only contains rows with the specified borough
def boroughfilter(transportation, borough, df, howmany):
    if transportation == "Walking":
        person = "PEDESTRIANS"
    elif transportation == "Biking":
        person = "CYCLISTS"
    else:
        person = "MOTORISTS"
    dfborough = df[df["BOROUGH"] == borough]
    remove_empty("ON STREET NAME", dfborough)

# grouping the ON STREET NAME and {person} INJURED columns by the ON STREET NAME values and summing them
    streetinjuries = (dfborough[["ON STREET NAME",f"{person} INJURED"]].groupby("ON STREET NAME").sum())

# sorting the values and only getting the first 3, 5, 10 values (whichever was specified by user)
    sorted = streetinjuries.sort_values(by=[f"{person} INJURED"], ascending=False)[0:howmany]
    return person, sorted

# creating bar chart for new borough dataframe
def bar(df, borough, transportation, color, howmany = 10):
    person, newdf = boroughfilter(transportation, borough, df, howmany)
    st.subheader(f"These are the top {howmany} streets to avoid!")
    bar = newdf.plot(kind = "barh", color = color)
    plt.title(f"Injuries from {transportation} in {borough.title()}", fontsize=15, fontweight="bold")
    x = np.arange(0, newdf[f"{person} INJURED"].max()+1, 1)
    plt.xticks(x)
    plt.xlabel("Number of Injuries", fontweight="bold", fontstyle="oblique")
    plt.ylabel("Street of Injuries", fontweight="bold", fontstyle="oblique")
    plt.grid(color='black', linestyle='--', linewidth=1, axis="x")
    plt.legend(facecolor = "beige")
    return plt

# function to filter the dataframe to a dataframe that only contains rows with the specified time
def timefilter(df, time):
    for value in df["TIME"]:
        if len(value) == 4:
            df["TIME"].replace(value, "0" + value, inplace=True)
    dftime = df[df["TIME"].str[0:2] == time[0:2]]
    dftime = dftime.drop(["ON STREET NAME", "PEDESTRIANS INJURED", "PEDESTRIANS KILLED", "CYCLISTS INJURED", "CYCLISTS KILLED",
                        "MOTORISTS INJURED", "MOTORISTS KILLED", "LOCATION", "LONGITUDE", "LATITUDE"], axis=1)
    remove_empty("BOROUGH", dftime)
    return dftime

# creating a map with the new dataframe
def timeMap(df, time):
    newdf = timefilter(df, time)
# grouping the BOROUGH and TIME columns by the BOROUGH values and counting them
    boroughCount = (newdf[["BOROUGH","TIME"]].groupby("BOROUGH").count())

# creating a list of the collision counts in each borough
    boroughCollisions = []
    for i in boroughCount["TIME"]:
        boroughCollisions.append(i)

# creating a list of the boroughs, lon, lats, collision counts
    locations = [("Bronx", 40.8448, -73.8648, boroughCollisions[0]), ("Brooklyn", 40.6782, -73.9442, boroughCollisions[1]),
                ("Manhattan", 40.7831, -73.9712, boroughCollisions[2]), ("Queens", 40.7282, -73.7949, boroughCollisions[3]),
                ("Staten Island", 40.5795, -74.1502, boroughCollisions[4])]

    dfmap = pd.DataFrame(locations, columns=["borough", "lat", "lon", "collisions"])

    view_state = pdk.ViewState(latitude=dfmap["lat"].mean(), longitude=dfmap["lon"].mean(), zoom=9, pitch=60)

    layer1 = pdk.Layer("ColumnLayer", data=dfmap, get_position='[lon, lat]', auto_Highlight = True, get_elevation= "collisions",
                        get_radius=10000, get_color=[200,200,200], pickable=True, extruded=True, elevationScale = 250, coverage=5,
                       diskResolution=8, wideframe=True)

    tool_tip = {"html" : "{borough}: {collisions} collisions"}

    map = pdk.Deck(initial_view_state=view_state, layers=[layer1], tooltip= tool_tip)

    st.pydeck_chart(map)

def main():
    from datetime import time

    df = pd.read_csv("collisions.csv")
    df.drop(["DATE", "UNIQUE KEY", "ZIP CODE", "CROSS STREET NAME", "OFF STREET NAME", "PERSONS INJURED",
            "PERSONS KILLED", "VEHICLE 1 TYPE", "VEHICLE 2 TYPE", "VEHICLE 3 TYPE", "VEHICLE 4 TYPE", "VEHICLE 5 TYPE",
             "VEHICLE 1 FACTOR", "VEHICLE 2 FACTOR", "VEHICLE 3 FACTOR", "VEHICLE 4 FACTOR", "VEHICLE 5 FACTOR"],inplace=True,axis=1)

# to remove a warning message
    pd.options.mode.chained_assignment = None

    from PIL import Image
    img = Image.open("nycstreets.jpeg")

    st.image(img, width=700)
    st.title("Welcome to the New York City Collision Monitor")

    st.header("What streets should you avoid?")
    st.subheader("Choose the borough you are traveling to")
# creating list of boroughs for selection
    boroughs = []
    remove_empty("BOROUGH", df)
    for b in df["BOROUGH"]:
        if b not in boroughs:
            boroughs.append(b)
# asking user to select a borough
    borough = st.selectbox('Borough: ', boroughs)
    st.subheader("What is your transportation method?")
# asking user for preferred method of transportation
    transportations = ['Walking', "Biking", "Driving"]
    transportation = st.radio("Select a mode of transportation: ", transportations)
# allowing user to customize the chart
    st.sidebar.header("Customize the chart!")
    st.sidebar.write("Do you want to see 3, 5, or 10 streets to avoid? (Please choose one option. If no option is chosen, default will be 10.)")
    three = st.sidebar.checkbox("3", False)
    five = st.sidebar.checkbox("5", False)
    ten = st.sidebar.checkbox("10", False)
    color = st.sidebar.color_picker("Pick a color for the bar chart")
    if three:
        howmany = 3
        st.pyplot(bar(df, borough, transportation, color, howmany))
    elif five:
        howmany = 5
        st.pyplot(bar(df, borough, transportation, color, howmany))
    elif ten:
        howmany = 10
        st.pyplot(bar(df, borough, transportation, color, howmany))
    else:
        st.pyplot(bar(df, borough, transportation, color))

    st.header("Which boroughs have the most collisions at what time?")
# asking user to select a time interval
    time = st.slider("Choose a time interval",time(0,00),time(23,00))
    time = time.strftime("%H:%M")
    timeMap(df, time)

main()
