from itertools import groupby
from pydoc import describe
import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data
import json
import time
st.set_page_config(layout="wide")

############################
### Metric Visualisation ###
############################

run = True
#@st.cache  # add caching so we load the data only once
def load_data(allow_output_mutation=True):
    metric_data = pd.read_csv('data/filtered_metrics_world_bank.csv')
    return metric_data

def get_selected_columns(df, metric, country):
    filtered_df = df 
    if (len(metric) > 0):
        filtered_df = filtered_df[filtered_df['Indicator Name'].isin(metric)]
    if (len(country) > 0):
        filtered_df = filtered_df[filtered_df['Country Name'].isin(country)]

    return filtered_df

st.header("Explore Metrics around the World\n\n")

metric_data = load_data()

cols = st.columns(2)
with cols[0]:
    metric = st.multiselect('Metric', metric_data['Indicator Name'].unique()) 
with cols[1]:
    country = st.multiselect('Country', metric_data['Country Name'].unique()) 

filtered_metrics = get_selected_columns(metric_data, metric, country)

# pivot the data to make years as rows
metric_data_filt = filtered_metrics.melt(id_vars=['Country Name', 'Indicator Name', 'Country Code', 'Indicator Code'], var_name='Year', value_name='Metric Data')
patternDel = "(Unnamed*)"
filter = metric_data_filt['Year'].str.contains(patternDel)
metric_data_filt = metric_data_filt[~filter]
# metric_data_filt = metric_data_filt.applymap(lambda x: isinstance(x, (int, float)))
# st.write(metric_data_filt)

line_chart_metric = alt.Chart(metric_data_filt,  title="Distribution of metrics").mark_line().encode(
    x='Year:T',
    y='Metric Data:Q',
    color='Country Name:N',
    tooltip='Metric Data:Q'
).properties(width=1000, height=500)

line_chart_metric








st.markdown("This project was created by Sayani, Ramya, Eeshwar and Sumanth for the [Interactive Data Science](https://dig.cmu.edu/ids2022) course at [Carnegie Mellon University](https://www.cmu.edu).")
