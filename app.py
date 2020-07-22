import streamlit as st
import pandas as pd
import numpy as np

st.title("COVID Toronto Location Visualization")

st.markdown(
"""
We have seen many dashboard apps that display COVID-19 data in aesthitic ways. 
However most of these dashboards were focused on displaying country level data. 

I decided to create this app to show what the infections rates were like in my hometown, Toronto.
This streamlit app explores which FSA has the most infection cases. A FSA or a 
Forward Sortation Area is a geographical region where all postal characters start with the same
three postal codes. In Toronto there are several FSAs that can be linked to different GPS
coordinates.

The data was provided on the Toronto Municpal website. Lets begin by opening the csv file.
"""
)

with st.echo():
    covid_df = pd.read_csv('COVID19 cases.csv')

st.write(covid_df.head())

st.markdown(
"""
There are many columns in this dataset but I'm mostly interested in the FSA column. THe three 
postal codes can be used to find the GPS coordinate we will later map to the map. 

We will group the data by FSA and use the count aggregate function to keep track of how many people were infectd
in a FSA.
"""
)

with st.echo():
    postal_covid = covid_df.groupby("FSA").count()["_id"]
    postal_covid = postal_covid.reset_index()
    postal_covid['lat'] = 0
    postal_covid['lon'] = 0

st.markdown(
"""
The next step is getting the GPS locations for the FSA.
Getting the FSA GPS data is incrediblely hard but I was able to use OSM data to retrive the data
into a csv file. Lets open the csv file and explore the data.
"""
)

with st.echo():
    postal_df = pd.read_csv('Postal Codes_2020071803700.csv')

st.write(postal_df.head())

st.markdown(
"""
The data is all squished up into one column. Even though the values are comma separated but pandas and
even excel had difficult separating it. We can seperate the values by using the dataframe.apply() method 
and use a function that splits the values by a comma into the respective row values.
"""
)

with st.echo():

    def extract_row(row):
        info = row["name"].split(",")
        row["place"] = info[-1]
        row["country"] = info[-2]
        row["geom_long"] = info[-3]
        row["geom_lat"] = info[-4]
        row["name"] = info[-5]

        return row

    postal_df = postal_df.apply(extract_row, axis=1)

st.write(postal_df.head())

st.markdown(
"""
The data now cleans but there is one more issue. The latitude and Longitude coordinates are being treated as a 
string. So we need to convert them into float values. Lets also join the FSA with their respective GPS locations in
this step.
"""
)

with st.echo():
    for index, row in postal_covid.iterrows():
        postal_row = postal_df[postal_df['name'] == row["FSA"]]
        postal_covid['lat'][index] = (postal_row['geom_lat'].values[0])
        postal_covid['lon'][index] = (postal_row['geom_long'].values[0])

    postal_covid['lat'] = postal_covid['lat'].astype(float)
    postal_covid['lon'] = postal_covid['lon'].astype(float)
    
    # Display the table
st.write(postal_covid)


st.markdown(
"""
We have the data ready now. We will dislplay it as a map for toronto with multiple points. The radius of the
points will determine the number infections in the FSA.
"""
)

midpoint = (np.average(postal_covid['lat']), np.average(postal_covid['lon']))

st.deck_gl_chart(
    viewport={
        'zoom': 10.5,
        'latitude': midpoint[0], 
        'longitude': midpoint[1],
        'pitch': 10,
    },  
    layers=[{
        'type': 'ScatterplotLayer',
        'data': postal_covid,
        'radiusScale': 2,
        'radiusMaxPixels': 100,
        'getRadius': "_id",
    }]
)
