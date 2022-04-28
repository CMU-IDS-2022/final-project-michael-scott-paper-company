from itertools import groupby
from pydoc import describe
import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data
st.set_page_config(layout="wide")
from iso3166 import Country
from IPython.display import display, HTML
alt.data_transformers.enable('default', max_rows =  None)
alt.data_transformers.disable_max_rows()

display(HTML("""
<style>
form.vega-bindings {
  position: absolute;
  right: 0px;
  top: 0px;
}
</style>
"""))

st.markdown(
    """
<style>
.sidebar .sidebar-content {
    background-image: linear-gradient(#2e7bcf,#2e7bcf);
    color: white;
}
</style>
""",
    unsafe_allow_html=True,
)

def do_intro():
    st.subheader(" No Country is safe from the impacts of climate change! According to research,\
         the carbon levels are at an all time high, the ice sheets in the poles are shrinking, \
            the weather anamolies are high throughout the globe. ")
    
    st.write("")
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.image("https://github.com/giswqs/data/raw/main/timelapse/spain.gif")

    with row1_col2:
        st.image("https://github.com/giswqs/data/raw/main/timelapse/las_vegas.gif")
    
    def get_line_chart(plot_df, yAxisLabel, yAxisTitle):
        trend = alt.Chart(plot_df).mark_line().encode(
            alt.X('year', axis=alt.Axis(title='Year')),
            alt.Y(yAxisLabel, axis=alt.Axis(title=yAxisTitle), scale=alt.Scale(zero=False))
        )
        return trend
    
    global_sea_level_file = "data/sea_level.csv" 
    global_sea_level = pd.read_csv(global_sea_level_file)
    sea_level_trend = get_line_chart(global_sea_level, 'sea_level', 'Sea level').properties(width=400, height=400)

    global_co2_file =  "data/co2.csv" 
    global_co2 = pd.read_csv(global_co2_file)
    global_co2 = global_co2[(global_co2['year'] > 1959) & (global_co2['year'] < 2022)]
    co2_trend = get_line_chart(global_co2, 'co2', 'CO2 emission').properties(width=400, height=400)

    global_temp_file =  "data/temp.csv" 
    global_temp = pd.read_csv(global_temp_file)
    temp_trend = get_line_chart(global_temp, 'temp', 'Global surface temperature').properties(width=400, height=400)

    ch = alt.vconcat(sea_level_trend, co2_trend, temp_trend)
    ch

countries = {}
for member_name, e in Country.__members__.items():
    countries[getattr(e, 'english_short_name').lower()] = getattr(e, 'numeric')

visualization = ("The Story",  "The Global Picture", "The Curious Case of Economy",
                   "The Exhaustive Story of Emissions",  "The Melting Ice Berg" )

# Using object notation
visual_type = st.sidebar.selectbox(
    "Which Visualization do you want to see?",
    visualization
)



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



def do_global_vis():

    st.title("Climate change analysis")

    st.subheader("Visualization 1")

    metric_data_filt = pd.read_csv("data/filtered_metric_data_with_income_status_four_groups.csv")

    metrics_needed = ['CO2 emissions (kt)', 'Electric power consumption (kWh per capita)', 'Total greenhouse gas emissions (kt of CO2 equivalent)', 'Forest area (sq. km)']

    metric_data_filt = metric_data_filt[metric_data_filt['Indicator Name'].isin(metrics_needed)]
    #input_dropdown = st.selectbox("Choose the Metric you want to visualize", metrics_needed)

    input_dropdown = alt.binding_select(options= metrics_needed, labels = metrics_needed, name = "Metric type: ")

    aggregated_data = metric_data_filt.groupby(["Year","status","Indicator Name"],as_index=False).agg({"Metric Data":"mean"})

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

def do_country_vis():
    def create_chart(country_data, picked):
        base1 = alt.Chart(country_data).encode(
            alt.X('Year', axis=alt.Axis(title=None))
        )

        area = base1.mark_area(opacity=0.3, color='#57A44C').encode(
            alt.Y('mean(Metric Data)',
            axis=alt.Axis(title='Avg. Temperature (°C)', titleColor='#57A44C')),
        ).transform_filter(picked)

        line = base1.mark_line(stroke='#5276A7', point = True).encode(
            alt.Y('mean(AbsoluteTemperature)',
                    axis=alt.Axis(title='Temperature', titleColor='#5276A7'),
                    scale=alt.Scale(zero=False)
            ),
            tooltip = 'mean(AbsoluteTemperature)'
        ).transform_filter(picked)


        joined = alt.layer(area, line).resolve_scale(
            y = 'independent'
        ).properties(width=200, height=200)
        return joined

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
    co2 = create_chart(country_data.loc[df_join_new['Indicator Name'] == 'CO2 emissions (kt)'], picked)
    electric = create_chart(country_data.loc[df_join_new['Indicator Name'] == 'Electric power consumption (kWh per capita)'], picked)
    greenhouse = create_chart(country_data.loc[df_join_new['Indicator Name'] == 'Total greenhouse gas emissions (kt of CO2 equivalent)'], picked)
    forest = create_chart(country_data.loc[df_join_new['Indicator Name'] == 'Forest area (sq. km)'], picked)


    joined = alt.vconcat((co2|electric), (greenhouse|forest))


    st.altair_chart(final_map | joined)
    return 

def do_ice_vis():
    st.subheader("Visualization 3")
    proj_temp_with_area = pd.read_csv("data/ice_area_temp.csv")
    
    range_ = [ 'darkgreen', 'lightgreen', 'orange', 'red', 'darkred','blue', 'skyblue','lightblue']
    proj_new_data = proj_temp_with_area.rename(columns={'Category': 'Year'})
    brush = alt.selection_single(fields=['SSP', 'SSPType'], on='mouseover', empty='none')
    base = alt.Chart(proj_new_data).encode(
        alt.X('Year:Q'),
    )
    ssp1_point = base.mark_point().encode(
        alt.Y('SSP:Q', scale=alt.Scale(zero=False)),
        alt.X('Year', scale=alt.Scale(zero=False)),
        alt.Color('SSPType'),
        strokeWidth=alt.value(2),
        tooltip = 'SSP'
    ).properties(width=700, height=400).add_selection(brush)

    ssp1_line = base.mark_line(
        point={
        "filled": True,
        }
    ).encode(
        alt.Y('SSP:Q', scale=alt.Scale(zero=False)),
        alt.X('Year', scale=alt.Scale(zero=False)),
        
        alt.Color('SSPType'),
        tooltip='SSP',
        strokeWidth=alt.value(2)
    )

    pie = alt.Chart(proj_new_data).mark_arc().encode(
        theta = alt.Theta(field="area", type="quantitative") ,
        color = alt.Color(field="area", type="nominal", scale=alt.Scale(range=range_)),
        radius = alt.datum(150, scale=None), 
        tooltip="area"
    ).transform_filter(brush).properties(width=400, height=400).add_selection(brush)

    # ssp1_line   
    (ssp1_point + ssp1_line) | pie 

def do_co2():
    
    st.subheader("CO2 emmissions - Biggest Contributors")
    st.markdown("The visualisation uncovers the emission rates of carbon dioxide across different continents.\
         The four charts visualise the four major years and the rates corresponding to the years.")
    co2_dist = pd.read_csv("data/co2_data.csv")
    continents = ["Asia", "Oceania", "North America", "South America", "Europe", "Africa"]
    
    continent = st.multiselect("Continent", continents,default=["North America"])

    if not continent:
        st.write("Please select at least one type of continent from the dropdown")
    else:
        co2_dist["year"] = co2_dist["year"].astype(str)
        co2_dist = co2_dist[co2_dist["country"].isin(continent)]
        co2_dist = co2_dist.groupby("year").sum()
        co2_dist = co2_dist.T.reset_index()[1:]

        y1 = alt.Chart(co2_dist).mark_bar().encode(
                x="1990",
                y=alt.Y('index', sort = "-x")
            )

        y2 = alt.Chart(co2_dist).mark_bar().encode(
                x = "2000",
                y = alt.Y('index', sort = "-x")
            )

        y3 = alt.Chart(co2_dist).mark_bar().encode(
                    x="2010",
                    y=alt.Y('index', sort = "-x")
                )

        y4 = alt.Chart(co2_dist).mark_bar().encode(
                    x="2019",
                    y=alt.Y('index', sort = "-x")
                )

        st.altair_chart((y1 | y2 ))
        st.altair_chart((y3 | y4))
    st.markdown("The visualisation digs deeper into the various green house gases.")
    metric_data_filt = pd.read_csv("data/green_house_gas.csv")
    chart = alt.Chart(metric_data_filt).mark_area().encode(
        y=alt.Y('sum(Metric Data)'),
        x='Year',
        color='Indicator Name',
        tooltip='sum(Metric Data)'
    ).properties(width=800, height=400)
    st.altair_chart(chart)


 



st.write(visual_type) 

if visual_type == visualization[1]:
    do_country_vis()
elif visual_type == visualization[2]:
    do_global_vis()
elif visual_type == visualization[3]:
    do_co2()
elif visual_type == visualization[4]:
    do_ice_vis()
elif visual_type == visualization[0]:
    do_intro()


st.markdown("This project was created by Sayani, Ramya, Eeshwar and Sumanth for the [Interactive Data Science](https://dig.cmu.edu/ids2022) course at [Carnegie Mellon University](https://www.cmu.edu).")
