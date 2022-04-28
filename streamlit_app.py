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

@st.cache
def read_df_from_file(filename):
    return pd.read_csv(filename)

def get_line_chart(plot_df, yAxisLabel, yAxisTitle):
    trend = alt.Chart(plot_df).mark_line().encode(
        alt.X('year', axis=alt.Axis(title='Year')),
        alt.Y(yAxisLabel, axis=alt.Axis(title=yAxisTitle), scale=alt.Scale(zero=False))
    )
    return trend

def do_intro():
    st.subheader("Climate change: causes and impact analysis")
    st.markdown(" According to research,\
         the carbon dioxide levels in atmosphere are at an all time high, the ice sheets in the poles are shrinking,\
            the weather anamolies are high throughout the globe. Hence, it is crucial for us to take the cliamte change issue seriously \
            and install plans to help ameliorate these effects and mitigate the issue by acting on the causes actively.")

    
    st.write("The two diagrams shown below depict the pace at which the world around us is changing! \
        On the left we can see the delta region in spain being submerged by sea level rise. \
            The right diagram depicts the changing landscape of vegas and the reduction in the water sources.")
    
    st.write("The two diagrams shown below depict the pace at which the world around us is changing! \
        On the left we can see the delta region in spain being submerged by sea level rise. \
            The right diagram depicts the changing landscape of vegas and the reduction in the water sources.")

   

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.image("https://github.com/giswqs/data/raw/main/timelapse/spain.gif", width=450)

    with row1_col2:
        st.image("https://github.com/giswqs/data/raw/main/timelapse/las_vegas.gif", width=430)

    st.subheader("Tangible effects of climate change")
    st.write("The following plots show some worrying trends in the effects of climate change in terms of numbers. \
    The first and most obvious effect is on temperature. As we all know, global temperatures have been rising over \
        decades and humans are the single most influential species in this change. As a direct result of this, \
            our polar ice caps are melting as well, causing an increase in sea levels.")
    
    def get_line_chart(plot_df, yAxisLabel, yAxisTitle):
        trend = alt.Chart(plot_df).mark_line().encode(
            alt.X('year', axis=alt.Axis(title='Year')),
            alt.Y(yAxisLabel, axis=alt.Axis(title=yAxisTitle), scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip(yAxisLabel, title =yAxisTitle)]
        )
        return trend
    st.markdown("The graphs below indicate the scale at which these issues are causing havoc in the ecosystem of earth.\
    The increasing trend in sea levels and global average temperature is alarming.")
      
    global_sea_level_file = "data/sea_level.csv" 
    global_sea_level = read_df_from_file(global_sea_level_file)
    sea_level_trend = get_line_chart(global_sea_level, 'sea_level', 'Sea level (mm)'
        ).properties(width=800, height=400
        ).configure_axis(
            labelFontSize=15,
            titleFontSize=15
        )


    global_temp_file =  "data/temp.csv" 
    global_temp = read_df_from_file(global_temp_file)
    temp_trend = get_line_chart(global_temp, 'temp', 'Global surface temperature (°C)'
        ).properties(width=800, height=400
        ).configure_axis(
            labelFontSize=15,
            titleFontSize=15
        )

    temp_trend
    sea_level_trend

countries = {}
for member_name, e in Country.__members__.items():
    countries[getattr(e, 'english_short_name').lower()] = getattr(e, 'numeric')

visualization = ("The Story",  "The Global Picture", "The Curious Case of Economy",
                   "The Exhaustive Story of Emissions",  "The Dwindling Ice Caps" )

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

    # st.title("Climate change analysis")
    st.subheader("How does a country's economic status affect metric trends?")
    # st.subheader("")

    metric_data_filt = read_df_from_file("data/filtered_metric_data_with_income_status_four_groups.csv")

    metrics_needed = ['CO2 emissions (kt)', 'Electric power consumption (kWh per capita)', 'Total greenhouse gas emissions (kt of CO2 equivalent)', 'Forest area (sq. km)']
    metric_data_filt = metric_data_filt[metric_data_filt['Indicator Name'].isin(metrics_needed)]
    #input_dropdown = st.selectbox("Choose the Metric you want to visualize", metrics_needed)
    st.markdown(f'<span style="color:blue">Interact-tip:</span> Select a metric type from the dropdown below and to visualize the values of CO2 emissions, electricity\
        electric power consumption, total greenhouse gas emissions and forest area. The data is aggregated by the income of the country.', unsafe_allow_html=True)
    input_dropdown = alt.binding_select(options= metrics_needed, labels = metrics_needed, name = "Metric type: ")

    aggregated_data = metric_data_filt.groupby(["Year","status","Indicator Name"],as_index=False).agg({"Metric Data":"mean"})

    picked = alt.selection_single(fields=["Indicator Name"], bind=input_dropdown, init={'Indicator Name': 'CO2 emissions (kt)'})
    line = alt.Chart(aggregated_data).mark_line(point=True).encode(
        alt.Color('status', title="Economic Status", sort=['High income', 'Upper middle income', 'Lower middle income', 'Low income']),
        alt.X('Year:O'),
        alt.Y('Metric Data', title="Metric Value"),
        tooltip='Metric Data'
    ).properties(
        width=700,
        height=500
    ).add_selection(picked).transform_filter(picked)

    st.altair_chart(line)

    # st.write("We would now like to explore whether the economic status of a country affects the various metrics that potentially affect the climate. In order to analyze this we have taken four categories of countries based on their income and plotted how the average value of each of the metrics have changed over that past 15 years.")

    # st.write("Some interesting insights that we got were:")

    st.write(" 1. The CO2 emission for high income countries can be seen decreasing indicating the policies\
         and steps they may have taken in the recent past to tackle the global warming problem. However, for\
              upper and lower middle income countries the emission skeep rising (yet to take actions to prevent \
                  this or effects not seen yet).\n2. We also observe that for all metrics except forest area the\
                       low income groups have a very low average value, indicating lesser industrialization \
                           in these areas.\n3. Electric power consumption also sees a similar trend with high\
                                income countries controlling the electric power consumption ( flattening curve)\
                                     whereas the rest still have an increasing trend.")


def do_country_vis():
    def create_chart(country_data, picked, metric_name):
        base1 = alt.Chart(country_data).encode(
            alt.X('Year', axis=alt.Axis(title=None))
        )

        area = base1.mark_area(opacity=0.3, color='#57A44C').encode(
            alt.Y('mean(Metric Data)',
            axis=alt.Axis(title=metric_name, titleColor='#57A44C')),
            tooltip=[alt.Tooltip('mean(Metric Data)', title=metric_name)]
        ).transform_filter(picked)

        line = base1.mark_line(stroke='#5276A7', point = True).encode(
            alt.Y('mean(AbsoluteTemperature)',
                    axis=alt.Axis(title='Temperature in degrees celsius', titleColor='#5276A7'),
                    scale=alt.Scale(zero=False)
            ),
            tooltip = [alt.Tooltip('mean(AbsoluteTemperature)', title="Temperature")]
        ).transform_filter(picked)


        joined = alt.layer(area, line).resolve_scale(
            y = 'independent'
        ).properties(width=300, height=200)
        return joined

    st.subheader("Temperature increase and its correlation with possible causes")
    st.write("")
    source = alt.topo_feature(data.world_110m.url, "countries")
    background = (
        alt.Chart(source)
        .mark_geoshape(fill="white", stroke="gray")
        .properties(width=800, height=500)
        .project("equirectangular")
    )

    df_join_new = read_df_from_file("data/Visualization_2_Data.csv")
    values = st.slider(
        'Select a range of years',
        1995, 2019, (2003, 2019)) 
    
    st.markdown("The visualisation below shows the global overview of increase in temperature scaled by the value of increase. The countries that are red have shown significant increase in tempearure.\
        We can select a particular country to view its statistics.  We try to correlate the trends in temperature increase with various possible factors.\
            We can evaluate the factors to check whether they are correlated. ")

    st.markdown(f'<span style="color:green">Analysis:</span> We want to understand the relative contribution of different countries to various cause of climate change such as carbon dioxide emissions,\
         electric power consumption, total greenhouse gas emissions and forest area.', unsafe_allow_html=True)
    st.markdown(f'<span style="color:blue">Interact-tip:</span> Select a time window and a country to view the temperature difference across years. The graphs on the right show the trend\
        of temperature change over the years along with the metrics mentioned above. This visualization helps analyze the correlation between temperature and other causal metrics', unsafe_allow_html=True)


    df_2012 = df_join_new[df_join_new['Year'] == values[0]]
    df_2013 = df_join_new[df_join_new['Year'] == values[1]]
    df_merged = df_2012.set_index('Country').join(df_2013.set_index('Country'), how='inner', lsuffix='_x', rsuffix='_y').reset_index()
    df_merged["Temperature difference"] = df_merged['TempDifference_y'] - df_merged['TempDifference_x']
    df_merged['Country'] = df_merged.apply(lambda x: transform_country(x['Country']), axis=1)
    df_merged['CountryCode'] = df_merged.apply(lambda x: get_country_code(x['Country']), axis=1)


    max_value = max(df_merged['Temperature difference'].max(), abs(df_merged['Temperature difference'].min()))
    df_merged['Temperature difference'] = round(df_merged['Temperature difference'], 3)
    picked = alt.selection_single(fields=["Country"])
    foreground = (
        alt.Chart(source)
        .mark_geoshape(stroke="black", strokeWidth=0.15)
        .encode(
            color = alt.condition(picked, 'Temperature difference:Q', alt.value("lightgray"), scale=alt.Scale(scheme="redblue", reverse=True, domain=[-max_value, max_value])),
            tooltip=[
                alt.Tooltip("Country:N", title="Country"),
                alt.Tooltip("Temperature difference:Q", title="Temperature Difference"),
            ],
        )
        .transform_lookup(
            lookup="id",
            from_=alt.LookupData(data=df_merged, key='CountryCode',fields=['Country', 'Temperature difference'])
        ).add_selection(picked)
    ).properties(width=400, height=500)


    final_map = (
        (background + foreground)
        .properties(width=800, height=500)
        .project("equirectangular")
    )

    country_data = df_join_new
    co2 = create_chart(country_data.loc[df_join_new['Indicator Name'] == 'CO2 emissions (kt)'], picked, "CO2 Emissions")
    electric = create_chart(country_data.loc[df_join_new['Indicator Name'] == 'Electric power consumption (kWh per capita)'], picked, "Electric power consumption")
    greenhouse = create_chart(country_data.loc[df_join_new['Indicator Name'] == 'Total greenhouse gas emissions (kt of CO2 equivalent)'], picked, "Total greenhouse gas emissions")
    forest = create_chart(country_data.loc[df_join_new['Indicator Name'] == 'Forest area (sq. km)'], picked, "Forest area")

    joined = alt.vconcat((co2|electric), (greenhouse|forest))
    st.altair_chart(final_map & joined)
    return 

def do_ice_vis():
    st.subheader("Projected temperature and Arctic Sea ice extent")
    st.write("In this page, we explore the effects of climate change on the average global surface temperature\
        and the effect on the ice extent in the Arctic Sea. For this, we have obtained projected values of\
        temperature from 'Shared Socioeconomic Pathways' (SSPs). The SSPs provide 5 pathways the world could take\
        ranging from a sustainability-focused growth to unconstrained growth in economic output and energy use.")

    st.write("Based on these temperature projections, we have trained a simple regression that predicts the\
        area of remaining ice extent in the Arctic sea. In some of the extreme cases such as SSP5, we see that\
        we might not have any ice caps left at the North Pole.")
    proj_temp_with_area = read_df_from_file("data/ice_area_temp.csv")
    st.markdown(f'<span style="color:blue">Interact-tip:</span> Select a point in line chart in one of the five SSP range line charts to view the corresponding ice sheet extent. The pie chart represents the amount of ice area (white) and the amount of water that has been melted(sky blue).', unsafe_allow_html=True)

    range_ = [ 'darkgreen', 'lightgreen', 'orange', 'red', 'darkred','blue']
    proj_new_data = proj_temp_with_area.rename(columns={'Category': 'Year'})
    proj_new_data = proj_new_data.replace({'SSP0': 'Measured temperature', 'SSP1': 'SSP 1', 'SSP2': 'SSP 2', 'SSP3': 'SSP 3', 'SSP4': 'SSP 4', 'SSP5': 'SSP 5', 'ice': 'Ice', 'water': 'Water'})
    proj_new_data = proj_new_data.rename(columns={'ssp_type': 'Natural resource', 'SSPType': 'Path'})
    brush = alt.selection_single(fields=['SSP', 'Path'], on='click', empty='none', init={'SSP': '9.61', 'Path':'SSP0'})
    base = alt.Chart(proj_new_data).encode(
        alt.X('Year:Q'),
    )


    ssp1_point = base.mark_point().encode(
        alt.Y('SSP:Q', scale=alt.Scale(zero=False),axis=alt.Axis(title='Surface temperature')),
        alt.X('Year', scale=alt.Scale(zero=False)),
        alt.Color('Path', legend=alt.Legend(
        orient='none',
        legendX=0, legendY=-40,
        direction='horizontal',
        titleAnchor='middle')),
        strokeWidth=alt.value(2),
        tooltip = 'area'
    ).properties(width=500, height=400).add_selection(brush)

    ssp1_line = base.mark_line(
        point={
        "filled": True,
        }
    ).encode(
        alt.Y('SSP:Q', scale=alt.Scale(zero=False)),
        alt.X('Year', scale=alt.Scale(zero=False)),
        
        alt.Color('Path'),
        tooltip='area',
        strokeWidth=alt.value(2)
    )

    pie_range = ['white', 'lightblue']
    pie = alt.Chart(proj_new_data).mark_arc().encode(
        theta = alt.Theta(field="area", type="quantitative") ,
        color = alt.Color(field="Natural resource", scale=alt.Scale(range=pie_range), legend=alt.Legend(
        orient='none',
        legendX=50, legendY=-40,
        direction='horizontal',
        titleAnchor='middle')),
        radius = alt.datum(150, scale=None), 
        tooltip="area"
    ).transform_filter(brush).properties(width=400, height=400).add_selection(brush)

    # ssp1_line   
    st.altair_chart(((ssp1_point + ssp1_line) | pie).resolve_scale(
        color='independent'
    ))
    # (ssp1_point + ssp1_line) | pie 

def do_co2():

    st.subheader("Greenhouse gas distribution")
    st.markdown("There is an increasing trend in the amount of greenhouse gases generated, mainly with a major increase in the amount of CO2 produced \
CO2 forms the major contributor to greenhouse gas emissions for any specific year. \
Oil, gas and coal are major contributors for the production of CO2, and are proportionately increasing over the years. This trend stays consistent across most continents. \
For Europe, Africa and North America, CO2 emissions due to coal have reduced over the years, and this might be because of steps taken to reduce emissions from traditional fuel sources such as coal.")
    st.markdown("The visualisation digs deeper into the various green house gases.")
    metric_data_filt = pd.read_csv("data/green_house_gas.csv")
    metric_data_filt = metric_data_filt.replace({'CO2 emissions (kt)': 'CO2 emissions', 'Methane emissions (kt of CO2 equivalent)': 'Methane emissions', 'Nitrous oxide emissions (thousand metric tons of CO2 equivalent)': 'Nitrous oxide emissions'})
    st.markdown(f'<span style="color:blue">Interact-tip:</span> The charts show the amount of individual green house gas emissions', unsafe_allow_html=True)

    chart = alt.Chart(metric_data_filt).mark_area().encode(
        y=alt.Y('sum(Metric Data)', axis = alt.Axis(title='Emission in kilo tons')),
        x='Year',
        color='Indicator Name',
        tooltip=[alt.Tooltip('sum(Metric Data)', title="Emission")]
    ).properties(width=800, height=400)
    st.altair_chart(chart) 

    st.subheader("CO2 emissions - Biggest Contributors")
    st.markdown("The visualisation uncovers the emission rates of carbon dioxide across different continents.\
         The four charts visualise the four major years and the rates corresponding to the years.")
    co2_dist = pd.read_csv("data/co2_data.csv")
    st.markdown(f'<span style="color:blue">Interact-tip:</span> Select the continents to filter on from the drop down to view the statistics for the set of the continents', unsafe_allow_html=True)

    continents = ["Asia", "Oceania", "North America", "South America", "Europe", "Africa"]
    
    continent = st.multiselect("Continent", continents,default=["North America"])

    co2_dist = co2_dist.rename(columns={'trade_co2': 'CO2 from trade', 'gas_co2': 'CO2 from gas', 'oil_co2': 'CO2 from oil', 'coal_co2': 'CO2 from coal', 'flaring_co2': 'CO2 from flaring', 'cement_co2': 'CO2 from cement', 'other_industry_co2': 'CO2 from other industries', 'consumption_co2': 'Total CO2 consumption'})

    if not continent:
        st.write("Please select at least one type of continent from the dropdown")
    else:
        co2_dist["year"] = co2_dist["year"].astype(str)
        co2_dist = co2_dist[co2_dist["country"].isin(continent)]
        co2_dist = co2_dist.groupby("year").sum()
        co2_dist = co2_dist.T.reset_index()[1:]

        y1 = alt.Chart(co2_dist).mark_bar().encode(
                x="1990",
                y=alt.Y('index', sort = "-x", title=""),
                tooltip = '1990',
            ).properties(
                width=320
            )

        y2 = alt.Chart(co2_dist).mark_bar().encode(
                x = "2000",
                y = alt.Y('index', sort = "-x", title=""),
                tooltip = '2000'
            ).properties(
                width=320
            )

        y3 = alt.Chart(co2_dist).mark_bar().encode(
                    x="2010",
                    y=alt.Y('index', sort = "-x", title=""),
                    tooltip = '2010'
                ).properties(
                width=320
            )

        y4 = alt.Chart(co2_dist).mark_bar().encode(
                    x="2019",
                    y=alt.Y('index', sort = "-x", title=""),
                    tooltip = '2019'
                ).properties(
                width=320
            )

        st.altair_chart((y1 | y2 ))
        st.altair_chart((y3 | y4))


 



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


st.markdown("Made with :heart: by Sayani, Ramya, Eeshwar and Sumanth for the [Interactive Data Science](https://dig.cmu.edu/ids2022) course at [Carnegie Mellon University](https://www.cmu.edu).")
