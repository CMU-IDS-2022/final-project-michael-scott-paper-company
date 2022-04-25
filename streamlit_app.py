from itertools import groupby
from pydoc import describe
import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data
# import json
# import time
st.set_page_config(layout="wide")

countries = {}
from iso3166 import Country
for member_name, e in Country.__members__.items():
    countries[getattr(e, 'english_short_name').lower()] = getattr(e, 'numeric')
# print(countries)

def transform_country(country):
  country = country.lower()
  if country == "united states":
    return "united states of america"
  if country == "russia":
    return "russian federation"
  if country == "venezuela":
    return "venezuela (bolivarian republic of)"
  if country == "tanzania":
    return "tanzania, united republic of"
  if country == "bonaire, saint eustatius and saba":
    return "bonaire, sint eustatius and saba"
  return country

def get_country_code(country):
    return countries.get(country.lower())

def create_chart(country_data):
  base1 = alt.Chart(country_data).encode(
      alt.X('Year', axis=alt.Axis(title=None))
  )

  area = base1.mark_area(opacity=0.3, color='#57A44C').encode(
      alt.Y('mean(Metric Data)',
      axis=alt.Axis(title='Avg. Temperature (°C)', titleColor='#57A44C')),
  ).transform_filter(picked)

  line = base1.mark_line(stroke='#5276A7', point = True).encode(
      alt.Y('mean(AbsoluteTemperature)',
            axis=alt.Axis(title='Temperature', titleColor='#5276A7')
      ),
      tooltip = 'mean(AbsoluteTemperature)'
  ).transform_filter(picked)


  joined = alt.layer(area, line).resolve_scale(
      y = 'independent'
  ).properties(width=200, height=200)
  return joined

st.title("Climate change analysis")

st.subheader("Visualization 1")

metric_data_filt = pd.read_csv("data/filtered_metric_data_with_status.csv")


metrics_needed = ['CO2 emissions (kt)', 'Electric power consumption (kWh per capita)', 'Total greenhouse gas emissions (kt of CO2 equivalent)', 'Forest area (sq. km)']

metric_data_filt = metric_data_filt[metric_data_filt['Indicator Name'].isin(metrics_needed)]
aggregated_data = metric_data_filt.groupby(["Year","status","Indicator Name"],as_index=False).agg({"Metric Data":"mean"})

input_dropdown = alt.binding_select(options= metrics_needed, labels = metrics_needed, name = "Metric type")
picked = alt.selection_single(fields=["Indicator Name"], bind=input_dropdown, init={'Indicator Name': 'CO2 emissions (kt)'})
line = alt.Chart(aggregated_data).mark_line(point=True).encode(
    alt.Color('status', scale=alt.Scale(scheme='pastel1')),
    alt.X('Year'),
    alt.Y('Metric Data'),
    tooltip='Metric Data'
).properties(
    width=700,
    height=500
).add_selection(picked).transform_filter(picked)

st.altair_chart(line)

st.subheader("Visualization 2")

source = alt.topo_feature(data.world_110m.url, "countries")
background = (
    alt.Chart(source)
    .mark_geoshape(fill="white", stroke="gray")
    .properties(width=600, height=300)
    .project("equirectangular")
).encode(
    # TODO: Remove this tooltip, added for debugging
    tooltip=[
            alt.Tooltip("id:N", title="ID"),
      ]
)

df_join_new = pd.read_csv("data/Visualization_2_Data.csv")
values = st.slider(
     'Select a range of years',
     1995, 2019, (2009, 2019))
df_2012 = df_join_new[df_join_new['Year'] == values[0]]
df_2013 = df_join_new[df_join_new['Year'] == values[1]]
df_merged = df_2012.set_index('Country').join(df_2013.set_index('Country'), how='inner', lsuffix='_x', rsuffix='_y').reset_index()
df_merged["TempDifference"] = df_merged['TempDifference_y'] - df_merged['TempDifference_x']
df_merged['Country'] = df_merged.apply(lambda x: transform_country(x['Country']), axis=1)
df_merged['CountryCode'] = df_merged.apply(lambda x: get_country_code(x['Country']), axis=1)


max_value = max(df_merged['TempDifference'].max(), abs(df_merged['TempDifference'].min()))
picked = alt.selection_single(fields=["Country"])
foreground = (
    alt.Chart(source)
    .mark_geoshape(stroke="black", strokeWidth=0.15)
    .encode(
        color = alt.condition(picked, 'TempDifference:Q', alt.value("lightgray"), scale=alt.Scale(scheme="redblue", reverse=True, domain=[-max_value, max_value])),
        tooltip=[
            alt.Tooltip("Country:N", title="Country"),
            alt.Tooltip("TempDifference:Q", title="Temperature Difference Per Year"),
        ],
    )
    .transform_lookup(
        lookup="id",
        from_=alt.LookupData(data=df_merged, key='CountryCode',fields=['Country', 'TempDifference'])
    ).add_selection(picked)
)


final_map = (
    (background + foreground)
    .properties(width=700, height=400)
    .project("equirectangular")
    # .project("orthographic")
)

country_data = df_join_new
co2 = create_chart(country_data.loc[df_join_new['Indicator Name'] == 'CO2 emissions (kt)'])
electric = create_chart(country_data.loc[df_join_new['Indicator Name'] == 'Electric power consumption (kWh per capita)'])
greenhouse = create_chart(country_data.loc[df_join_new['Indicator Name'] == 'Total greenhouse gas emissions (kt of CO2 equivalent)'])
forest = create_chart(country_data.loc[df_join_new['Indicator Name'] == 'Forest area (sq. km)'])


joined = alt.vconcat((co2|electric), (greenhouse|forest))


st.altair_chart(final_map | joined)

st.subheader("Visualization 3")

# TODO: Complete this after getting the data

def positive_vibes(status,data_renewable):
    status_data = data_renewable[data_renewable["status"]==status]
    line = alt.Chart(status_data).mark_line(point=True).encode(
        alt.Color('status', scale=alt.Scale(scheme='pastel1')),
        alt.X('Year'),
        alt.Y('Metric Data'),
        tooltip='Metric Data'
    ).properties(
        width=700,
        height=500
    )


# final_map

st.markdown("This project was created by Sayani, Ramya, Eeshwar and Sumanth for the [Interactive Data Science](https://dig.cmu.edu/ids2022) course at [Carnegie Mellon University](https://www.cmu.edu).")



