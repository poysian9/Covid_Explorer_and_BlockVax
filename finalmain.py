import copy
import datetime
import math
import os
import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib.backends.backend_agg import RendererAgg
import plotly.express as px
from numpy import nan as Nan
from sklearn.linear_model import LinearRegression
from plotly.subplots import make_subplots
import plotly.graph_objects as go
plt.rcParams['figure.figsize'] = 10, 12
import warnings
warnings.filterwarnings('ignore')
import seaborn as sns
from PIL import Image

# todo states where cases and deaths are most and least correlated


st.set_page_config(
    page_title="Covid-19 Forecast and Correlation Explorer",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache(suppress_st_warning=True)
def process_data(country):
    """
    Process CSVs. Smooth and compute new series.
    :param state: Selected Country
    :return: Dataframe
    """
    # Data
    df = (pd.read_csv("Data/owid-covid-data.csv")
            .sort_values("date", ascending=True)
            .reset_index()
            .query('location=="{}"'.format(country))
          )
    
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df = df.query("date >= '2020-03-01' ")
    df.set_index("date", inplace=True)

    # Rolling means
    df["new_tests"] = df["new_tests"].rolling(7).mean()
    df["total_deaths"] = df["total_deaths"].rolling(7).mean()
    df["new_deaths"] = df["new_deaths"].rolling(7).mean()
    df["hosp_patients"] = df["hosp_patients"].rolling(7).mean()
    df["total_tests"] = df["total_tests"].rolling(7).mean()
    df["icu_patients"] = df["icu_patients"].rolling(7).mean()
    df["cardiovasc_death_rate"] = df["cardiovasc_death_rate"].rolling(7).mean()
    df["total_cases"]=df["total_cases"].rolling(7).mean()

    # New features
    df["percentPositive"] = (
        (df["new_tests"] / df["total_tests"]).rolling(7).mean()
    )
    
    df = calc_prevalence_ratio(df)

    df["Infection Fatality Rate"] = (
        df["new_deaths"] / (df["new_cases"] * df["prevalence_ratio"])
    ) * 100
    df["percentPositive"] = df["percentPositive"] * 100
    df["Cumulative Recovered Infections Estimate"] = (
        df["total_cases"] * df["prevalence_ratio"] - df["total_deaths"]
    )
    
    if np.inf in df.values:
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
    return df


def calc_prevalence_ratio(df):
    """
    Calculate prevalence ratio
    prevalence_ratio(day_i) = (1250 / (day_i + 25)) * (positivity_rate(day_i))^(0.5) + 2, where day_i is the number of days since    February 12, 2020.
    https://covid19-projections.com/estimating-true-infections-revisited/
    :param df: Dataframe from process_data()
    :return: Dataframe with prevalence_ratio column
    """

    days_since = df.index - datetime.datetime(year=2020, month=2, day=12)
    df["days_since_feb12"] = days_since.days.values
    p_r_list = []
    for i, row in df.iterrows():
        try:
            prevalence_ratio = (1250 / (row['days_since_feb12'] + 25)) * math.pow(row['percentPositive'], 0.5) + 2
            # prevalence_ratio = (1500 / (row["days_since_feb12"] + 50)) * math.pow(
            #     row["percentPositive"], 0.5
            # ) + 2
            #prevalence_ratio = (1000 / (row["days_since_feb12"] + 10)) * math.pow(row["percentPositive"], 0.5) + 2
            # st.write(prevalence_ratio)
        except:
            prevalence_ratio = p_r_list[-1]
        p_r_list.append(prevalence_ratio)
        # st.write(prevalence_ratio)
    df["prevalence_ratio"] = p_r_list
    return df


@st.cache()
def find_max_correlation(col, col2):
    """
    Take two series and test all alignments for maximum correlation.
    :param col: Column 1
    :param col2: Column 2
    :return: Best r, best shift
    """
    best_cor = -1
    best_i = 0
    for i in range(len(col) // 5):
        col1 = col.shift(i)
        correl = col1.corr(col2)
        if correl > best_cor:
            best_cor = correl
            best_i = i

    return best_cor, best_i


def plot_cor(col, col2, best_i, best_cor):
    """
    Plot interactive chart showing correlation between two shifted series.
    :param col:
    :param col2:
    :param best_i:
    :param best_cor:
    """
    # st.line_chart({col.name: col.shift(best_i), col2.name: col2})
    st.write(
        "{} shifted {} days ahead is correlated with {}. $r={}$".format(
            col.name, best_i, col2.name, round(best_cor, 2)
        )
    )

    # altair chart
    src = pd.DataFrame({col.name: col.shift(best_i), col2.name: col2}).reset_index()
    base = alt.Chart(src).encode(alt.X("date:T", axis=alt.Axis(title=None)))

    line = base.mark_line(stroke="orange").encode(
        alt.Y(col.name, axis=alt.Axis(title=col.name, titleColor="orange"))
    )

    line2 = base.mark_line(stroke="#5276A7").encode(
        alt.Y(col2.name, axis=alt.Axis(title=col2.name, titleColor="#5276A7"))
    )

    chrt = alt.layer(line, line2).resolve_scale(y="independent")
    st.altair_chart(chrt, use_container_width=True)


# @st.cache(ttl=TTL)
def get_shifted_correlations(df, cols):
    """
    Interactive correlation explorer. For two series, finds the alignment that maximizes correlation.
    :param df:
    :param cols:
    :return:
    """
    a = st.selectbox("Does this", cols, index=3)
    b = st.selectbox("Correlate with this?", cols, index=2)
    lb = st.slider(
        "How far back should we look for correlations?",
        min_value=0,
        max_value=len(df),
        value=len(df) - 90,
        step=10,
        format="%d days",
        key="window2",
    )

    cor, shift = find_max_correlation(df[a].iloc[-lb:], df[b].iloc[-lb:])
    col1, col2 = df[a].iloc[-lb:], df[b].iloc[-lb:]
    plot_cor(df[a].iloc[-lb:], df[b].iloc[-lb:], shift, cor)

    return cols, a, b, lb


def get_correlations(df, cols):
    st.header("Correlations")
    df = df[cols]
    cor_table = df.corr(method="pearson", min_periods=30)
    st.write(cor_table)
    max_r = 0
    max_idx = None
    seen = []
    cors = pd.DataFrame(columns=["a", "b", "r"])
    for i in cor_table.index:
        for j in cor_table.index:
            if i == j or i == "index" or j == "index":
                continue
            if cor_table.loc[i, j] == 1:
                continue
            if cor_table.loc[i, j] > max_r:
                max_idx = (i, j)
                max_r = max(cor_table.loc[i, j], max_r)
            if (j, i) not in seen:
                cors = cors.append(
                    {"a": i, "b": j, "r": cor_table.loc[i, j]}, ignore_index=True
                )
                seen.append((i, j))
    st.write(max_idx, max_r)
    st.write(cors.sort_values("r", ascending=False).reset_index(drop=True))

def linearRegression(df,country):
    selected_columns=['iso_code', 'location', 'date', 'total_cases', 'new_cases', 'total_deaths','new_deaths','icu_patients','hosp_patients','new_tests', 'total_tests', 'total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated', 'new_vaccinations']    
    new_df = df.loc[:, selected_columns]
    day = df[df['location'] == country].groupby('date')[['total_cases']].sum()
    x = np.arange(len(day))
    y= day.values
    x = x.reshape(-1,1)
    model = LinearRegression()
    model.fit(x,y)
    Yp=model.predict(x)        
    st.header(f"Predict COVID Cases trend in {country} using Linear Regression")
    fig = plt.figure()    
    ax = fig.add_subplot(2,2,1)
    ax.scatter(x,y)
    ax.plot(x,Yp)
    ax.set_xlabel("Days")
    ax.set_ylabel("Nummber of Cases")
    st.pyplot(fig)       
    st.header(f"Predict Vaccination trend in {country} using Linear Regression")
    vac = df[df['location'] == country].groupby('date')[['people_fully_vaccinated']].sum()
    x1 = np.arange(len(vac))
    y1 = vac.values
    x1 =x1.reshape(-1,1)
    model.fit(x1,y1)
    Yp1=model.predict(x1)            
    fig = plt.figure()
    ax = fig.add_subplot(2,2,2)
    ax.scatter(x1,y1)
    ax.plot(x1,Yp1)
    ax.set_xlabel("Days")
    ax.set_ylabel("Nummber of People Vaccinated")
    st.pyplot(fig)    

#TimeSeries Analaysis

def TimeSeries(country,country1,df):
    df_country= df.sort_values("date", ascending=True).reset_index().query('location=="{}"'.format(country))
    df_country['date'] = pd.to_datetime(df_country['date'], format='%Y-%m-%d')
    df_country = df_country.query("date >= '2020-02-01' ")            
    df_country1 = df.sort_values("date", ascending=True).reset_index().query('location=="{}"'.format(country1))
    df_country1['date'] = pd.to_datetime(df_country1['date'], format='%Y-%m-%d')
    df_country1 = df_country1.query("date >= '2020-02-01' ")                
    
    fig = px.bar(df_country, x="date", y="total_cases", color='total_cases', height=600, title=f'Total Confirmed Coronavirus Cases in {country}',color_discrete_sequence = px.colors.cyclical.IceFire)
    st.plotly_chart(fig)
    fig = px.bar(df_country1, x="date", y="total_cases", color='total_cases', orientation='v', height=600,
            title=f'Total Confirmed Coronavirus Cases in {country1}', color_discrete_sequence = px.colors.cyclical.IceFire)

    st.plotly_chart(fig)
    
def cumulativeCases(country1,country2,df):
    df_country1= df.sort_values("date", ascending=True).reset_index().query('location=="{}"'.format(country1))
    df_country1['date'] = pd.to_datetime(df_country1['date'], format='%Y-%m-%d')
    df_country1 = df_country1.query("date >= '2020-02-01' ")            
    df_country2 = df.sort_values("date", ascending=True).reset_index().query('location=="{}"'.format(country2))
    df_country2['date'] = pd.to_datetime(df_country2['date'], format='%Y-%m-%d')
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{}, {}],
           [{"colspan": 2}, None]],
    subplot_titles=(country1,country2))

    fig.add_trace(go.Bar(x=df_country1['date'], y=df_country1['total_cases'],
                    marker=dict(color=df_country1['total_cases'], coloraxis="coloraxis")),1, 1)

    fig.add_trace(go.Bar(x=df_country2['date'], y=df_country2['total_cases'],
                    marker=dict(color=df_country2['total_cases'], coloraxis="coloraxis")),1, 2)
    
    fig.update_layout(coloraxis=dict(colorscale='Bluered_r'), showlegend=False,title_text="Total Confirmed cases(Cumulative)")

    fig.update_layout(plot_bgcolor='rgb(230, 230, 230)')
    st.plotly_chart(fig)

def covidTrend(country1,country2,df):    
    df_country1= df.sort_values("date", ascending=True).reset_index().query('location=="{}"'.format(country1))
    df_country1['date'] = pd.to_datetime(df_country1['date'], format='%Y-%m-%d')
    df_country1 = df_country1.query("date >= '2020-02-01' ")            
    df_country2 = df.sort_values("date", ascending=True).reset_index().query('location=="{}"'.format(country2))
    df_country2['date'] = pd.to_datetime(df_country2['date'], format='%Y-%m-%d')    
    fig = make_subplots(rows=2, cols=2, specs=[[{}, {}], [{"colspan": 2}, None]], subplot_titles=(country1,country2))
    fig.add_trace(go.Scatter(x=df_country1['date'], y=df_country2['new_cases'], marker=dict(color=df_country1['total_cases'], coloraxis="coloraxis")), 1, 1)
    fig.add_trace(go.Scatter(x=df_country2['date'], y=df_country2['new_cases'], marker=dict(color=df_country2['total_cases'], coloraxis="coloraxis")), 1, 2)
    fig.update_layout(coloraxis=dict(colorscale='Bluered_r'), showlegend=False,title_text="Trend of New Coronavirus cases")
    fig.update_layout(plot_bgcolor='rgb(250, 242, 242)')
    st.plotly_chart(fig)

def explorerData(df_country):
    st.title("Welcome to the Covid-19 Tracker Application")
    st.markdown("""    
    """)
        # Summary Table

    st.header(f'Summary Table for the last {table_days} days.')
    
    st.markdown(""" This table includes the number of cases, deaths, new cases and moving average for your selection.""")

    #st.write(df_county.iloc[-table_days:,-4:])

    a = df_country.iloc[-table_days:, -4:]
    
    my_table = st.table(a)


    # Total Cases Graph

    st.header(f'Total Cases for {country}.')
    
    total_cases_chart = df_country['total_cases']

    
    st.line_chart(total_cases_chart)

    
    # Moving Average Graph

    st.header(f'{moving_average_day} moving average for {country}.')
    
    moving_average_chart = df_country['moving_average']
    
    st.line_chart(moving_average_chart)

    
    # Death Graph

    st.header(f'Total Deaths for {country}.')
    
    total_deaths_chart = df_country['total_deaths']
    
    st.line_chart(total_deaths_chart)    

#Solidity Example

#main function
if __name__ == "__main__":    
    # todo global cols lists. One for cors and one for UI
    cols = [
        "Infection Fatality Rate",
        "new_cases",
        "new_deaths",
        "hosp_patients",
        "icu_patients",
        "percentPositive",
        "total_tests",        
    ]    
    
    w, h, = (
        900,
        400,
    )
    df_covid= pd.read_csv("Data/owid-covid-data.csv")
    countries = pd.read_csv("Data/owid-covid-data.csv")["location"].unique()

    with st.sidebar:
        st.title("Covid-19 Data Explorer")
        st.subheader("Select a page below:")
        mode = st.radio(
            "Menu",
            [
                "COVID Explorer",
                "Correlation Explorer",
                "Linear Regression",
                "TimeSeries Analysis",
                "BlockVax"
            ],
        )
        st.subheader("Select a Country:")        
        country = st.selectbox("",countries, index=37)

    # https://docs.streamlit.io/en/stable/troubleshooting/caching_issues.html#how-to-fix-the-cached-object-mutated-warning
    df = copy.deepcopy(process_data(country))    

    if mode == "COVID Explorer":        
        st.sidebar.header("Covid-19 Data Explorer")                
        #country = st.sidebar.selectbox('Select Your Country:',countries)     
        table_days = st.sidebar.slider('Select the number of days you want to be display in the Summary Table. ', min_value = 3, max_value= 15, value= 5, step=1)
        moving_average_day = st.sidebar.slider('How many days to consider for the moving average? ', min_value = 5, max_value = 14, value = 7, step=1)
        # Creating the dataframe for the country
        df_country = df_covid[(df_covid.location == country)].copy()
    
        #Create a new column for 7-day moving average
        df_country['moving_average'] = df_country.loc[:,'new_cases'].rolling(window=moving_average_day).mean()
        if (country != ""):
            explorerData(df_country)
    elif mode == "Correlation Explorer":
        st.title("Interactive Correlation Explorer")
        st.write("Choose two variables and see if they are correlated.")
        cols, a, b, lookback = get_shifted_correlations(df, cols)    
    elif mode =="Linear Regression":        
        linearRegression(df_covid,country)
    elif mode =="TimeSeries Analysis":        
        st.sidebar.subheader("Select a Comparison Country:")        
        country1 = st.sidebar.selectbox("",countries, index=45)
        if (country == country1):
            st.write("Please select different Comparison Country")
        elif (country != "" and country1 !=""):
            TimeSeries(country,country1,df_covid)
            #cumulativeCases(country,country1,df_covid)
            covidTrend(country,country1,df_covid)
    elif mode == "BlockVax":
            st.title("Introducing BlockVax - Profile and Vaccine Data Registration")
            st.subheader("\n")
            
            st.markdown("""
                    BlockVax is a smart contract which interacts with the ethereum network to allow users to register a profile for themselves or others, generating a unique patient ID number and storing the profile data in a profile struct as part of a mapping. Their profile registration will require their address as well as a photo ID, which will be uploaded to [pinata](https://pinata.cloud/) and stored via an IPFS hash.
                    """)
            img = Image.open("Images\image1.png")
            st.image(img, width=200)                    
            st.image("Images\image2.png", width=200)
                    
                    
            st.markdown(""" 
                Once a profile has been created, registered vaccine providers are able to update vaccine data of vaccinated patients by using the patient's address and ID number and photo URI as part of our token JSON scehma shown below. """)
                    
            st.image("Images\image3.png", width=200)
                    
                    
            st.write("This function will then mint a non-fungible token using the patient's address and ID number and set the token URI, as well as update the patient's profile with the vaccine data.")                  
            st.image("Images\image4.png", width=200)
                    
            st.write("Modifier's were created to restrsict function access and to ensure only the right data can be inputted, since this contract interacts with a blockchain and hence immutable, we do not want to waste gas fees on data errors or accidentally input incorrect data.")
                    
            st.markdown(""" Requirements include:
                        * Restriction of provider function use to only providers registered in the contract
                        * The vaccine name having to match our stored vaccine names
                        * Only valid patient IDs
                        * Only registered/valid patient addresses can be inputted
                    """)
            st.image("Images\image5.png", width=200)
                    
            st.image("Images\image6.png", width=200)
                    
            st.markdown("""Finally, our last function allows the user to search for a patient ID and check if they've been vaccinated.                     
                    """)
            st.image("Images\image7.png", width=200)
