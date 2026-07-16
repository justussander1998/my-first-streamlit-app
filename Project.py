# -*- coding: utf-8 -*-
"""
Spyder-Editor

Dies ist eine temporäre Skriptdatei.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.io as pio

pio.templates.default = 'plotly_white'


st.set_page_config(page_title="Project Justus C. Sander",page_icon="⚽", layout="wide")
st.title("Project Justus C. Sander")
st.write("⚽ Analysis of a football match dataset ⚽")

# loading the data and caching it for speed
@st.cache_data
def load_data():
    return pd.read_csv("Matches.csv.gz")

# function call
matches = load_data()

# Remove Betting columns
betting_data = ['OddHome', 'OddDraw', 'OddAway', 'MaxHome', 'MaxDraw', 'MaxAway', 
              'Over25', 'Under25', 'MaxOver25', 'MaxUnder25', 'HandiSize', 'HandiHome', 'HandiAway', 'C_LTH', 'C_LTA', 'C_VHD', 'C_VAD', 'C_HTB', 'C_PHB']
matches.drop(columns=betting_data, inplace=True)

# Combine MatchDate and MatchTime
matches['MatchTime'] = matches['MatchTime'].fillna('00:00:00')
matches['MatchDateTime'] = pd.to_datetime(matches['MatchDate'] + ' ' + matches['MatchTime'])
cols = ['MatchDateTime'] + [col for col in matches.columns if col != 'MatchDateTime']
matches = matches[cols]

#Change league names
league_names = {
    'E0': 'England Premier League',
    'E1': 'England Championship',
    'E2': 'England League One',
    'E3': 'England League Two',
    'EC': 'England Conference',
    'SC0': 'Scotland Premiership',
    'SC1': 'Scotland Championship',
    'SC2': 'Scotland League One',
    'SC3': 'Scotland League Two',
    'D1': 'Germany Bundesliga',
    'D2': 'Germany 2. Bundesliga',
    'I1': 'Italy Serie A',
    'I2': 'Italy Serie B',
    'SP1': 'Spain La Liga',
    'SP2': 'Spain Segunda Division',
    'F1': 'France Ligue 1',
    'F2': 'France Ligue 2',
    'N1': 'Netherlands Eredivisie',
    'B1': 'Belgium First Division A',
    'P1': 'Portugal Primeira Liga',
    'T1': 'Turkey Super Lig',
    'G1': 'Greece Super League',
    'ARG': 'Argentina Primera Division',
    'USA': 'USA MLS',
    'BRA': 'Brazil Serie A',
    'JAP': 'Japan J League',
    'MEX': 'Mexico Liga MX',
    'ROM': 'Romania Liga I',
    'POL': 'Poland Ekstraklasa',
    'SWE': 'Sweden Allsvenskan',
    'NOR': 'Norway Eliteserien',
    'RUS': 'Russia Premier League',
    'DEN': 'Denmark Superliga',
    'CHN': 'China Super League',
    'IRL': 'Ireland Premier Division',
    'FIN': 'Finland Veikkausliiga',
    'AUT': 'Austria Bundesliga',
    'SUI': 'Switzerland Super League'
}

matches['Division'] = matches['Division'].replace(league_names)

#Remove leagues which don' start in summer
calendar_year_leagues = [
    'USA MLS',
    'Brazil Serie A',
    'Japan J League',
    'China Super League',
    'Argentina Primera Division',
    'Sweden Allsvenskan',
    'Norway Eliteserien',
    'Finland Veikkausliiga',
    'Ireland Premier Division'
]
matches = matches[~matches['Division'].isin(calendar_year_leagues)]

def get_season(date):
    year = date.year
    if date.month >= 8:  # August or later
        return f"{year}/{str(year+1)[2:]}"
    else:  # Januar until Juli
        return f"{year-1}/{str(year)[2:]}"

matches['Season'] = matches['MatchDateTime'].apply(get_season)

#Games before August 2000 are matched with the wrong season
matches.loc[matches['Season'] == '1999/00', 'Season'] = '2000/01'

matches['MatchHour'] = matches['MatchDateTime'].dt.hour
matches['TotalGoals'] = matches['FTHome'] + matches['FTAway'] #include the total goal number per game
matches['TotalShotsOnTarget'] = matches['HomeTarget'] + matches['AwayTarget']
matches['TotalYellow'] = matches['HomeYellow'] + matches['AwayYellow']
matches['TotalRed'] = matches['HomeRed'] + matches['AwayRed']


st.header("Sample of cleaned data")
st.dataframe(matches.tail())

top5_leagues = [
    'Germany Bundesliga', 
    'France Ligue 1', 
    'England Premier League', 
    'Spain La Liga', 
    'Italy Serie A'
]

# Link for Dataset 
st.sidebar.markdown("[📊 Dataset Source](https://www.kaggle.com/code/mahmoudredagamail/club-football-match-data-2000-2025)")
st.sidebar.write("Owner: Mahmoud Gamil")
st.sidebar.write("Accessed: 09.07.2026, 13:23")

# adding side bar with filters
st.sidebar.header("Filter Data")

# Button: Top 5 Leagues yes/no
top5_only = st.sidebar.toggle("Show only Top 5 Leagues", value=False)

# Season-Auswahl (von xx bis yy)
all_seasons = sorted(matches["Season"].unique())
selected_seasons = st.sidebar.select_slider(
    "Select season range:",
    options=all_seasons,
    value=(all_seasons[0], all_seasons[-1])
)

# Liga-Auswahl (Multiselect)
if top5_only:
    league_options = top5_leagues
else:
    league_options = matches["Division"].unique()

selected_leagues = st.sidebar.multiselect(
    "Select leagues:", 
    league_options, 
    default=league_options
)

# Gefilterte Daten basierend auf allen Widgets
season_index_start = all_seasons.index(selected_seasons[0])
season_index_end = all_seasons.index(selected_seasons[1])
seasons_in_range = all_seasons[season_index_start:season_index_end + 1]

boolean_filter = (
    matches["Division"].isin(selected_leagues) & 
    matches["Season"].isin(seasons_in_range)
)
filtered = matches.loc[boolean_filter]

# Calculate metrics using pandas
num_matches = len(filtered)
sum_goals = filtered["TotalGoals"].sum()
avg_goals = filtered["TotalGoals"].mean()
sum_yellow = filtered["TotalYellow"].sum()
avg_yellow = filtered["TotalYellow"].mean()
avg_red = filtered["TotalRed"].mean()
sum_red = filtered["TotalRed"].sum()

# display metrics using streamlit
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Number of Matches", value=f"{num_matches:,}")
col2.metric(label="Total Goals", value=f"{sum_goals:,.0f}")
col2.metric(label="Avg. Goals", value=f"{avg_goals:,.2f}")
col3.metric(label="Total Yellow cards", value=f"{sum_yellow:,.0f}")
col3.metric(label="Avg. Yellow cards", value=f"{avg_yellow:,.2f}")
col4.metric(label="Total Red cards", value=f"{sum_red:,.0f}")
col4.metric(label="Avg. Red cards", value=f"{avg_red:,.2f}")

# Figure 1
df_q1 = filtered[['Division', 'TotalGoals']].dropna()
df_q1 = df_q1.groupby('Division')['TotalGoals'].mean().reset_index()
df_q1.columns = ['Division', 'AvgGoals']

fig_q1a = px.bar(
    data_frame=df_q1,
    x='Division',
    y='AvgGoals',
    title="Average Goals per Match sorted by league",
    labels={"Division": " ", "AvgGoals": "Average Goals"},
    text_auto='.2f'
)
fig_q1a.update_xaxes(categoryorder='total descending')
fig_q1a.update_yaxes(range=[2, 3.2])

# Figure 2
df_q2 = filtered[['Division', 'TotalGoals', 'Season']].dropna()
df_q2 = df_q2.groupby(['Division', 'Season'])['TotalGoals'].mean().reset_index()
df_q2.columns = ['Division', 'Season', 'Average Goals']

fig_q2 = px.line(
    data_frame=df_q2,
    x="Season",
    y="Average Goals",
    hover_name='Division',
    color='Division',
    color_discrete_sequence=px.colors.qualitative.Safe,
    markers=True,
    title="Average Goals per match for the season 2000/01 until 2024/25",
    height=500
)
fig_q2.update_layout(
    width=2000,
    legend_title_text=' '
)
fig_q2.update_xaxes(
    title="Season",
    tickangle=45,
    categoryorder='array',
    categoryarray=sorted(df_q2['Season'].unique())
)
fig_q2.update_yaxes(
    title="Average Goals per Match",
    gridcolor='lightgrey'
)

# Figure 3
df_q3 = filtered[['Division', 'Season', 'TotalShotsOnTarget']].dropna()
df_q3 = df_q3.groupby(['Division', 'Season'])['TotalShotsOnTarget'].mean().reset_index()
df_q3.columns = ['Division', 'Season', 'Average Shots on Target']

fig_q3 = px.line(
    data_frame=df_q3,
    x="Season",
    y="Average Shots on Target",
    hover_name='Division',
    color='Division',
    color_discrete_sequence=px.colors.qualitative.Safe,
    markers=True,
    title="Average Shots on Target per match",
    height=500
)
fig_q3.update_layout(
    width=1200,
    legend_title_text=' '
)
fig_q3.update_xaxes(
    title="Season",
    tickangle=45,
    categoryorder='array',
    categoryarray=sorted(df_q3['Season'].unique())
)
fig_q3.update_yaxes(
    title="Average Shots on target per Match",
    gridcolor='lightgrey'
)


# Figure 4
df_q4 = filtered[['Division', 'MatchHour', 'TotalGoals']].dropna()
df_q4 = df_q4[df_q4['MatchHour'] != 0]
df_q4.columns = ['Division', 'Match Time (by hour)', 'Total Goals']

fig_q4a = px.box(
    data_frame=df_q4,
    x='Match Time (by hour)',
    y='Total Goals',
    hover_name='Division',
    color='Division',
    title="Distribution of Goals by Kickoff Time",
    labels={"Match Time (by hour)": "Kickoff Hour", "Total Goals": "Total Goals per Match", "Division": "League"},
    color_discrete_sequence=px.colors.qualitative.Safe
)
fig_q4a.update_layout(
    width=1200,
    height=600,
    legend_title_text='League'
)
fig_q4a.update_xaxes(
    title="Kickoff Hour",
    dtick=1
)
fig_q4a.update_yaxes(
    title="Total Goals per Match",
    gridcolor='lightgrey'
)

# Figure 5
df_q5 = filtered[['Division', 'FTResult']].dropna()
df_q5 = df_q5.groupby(['Division', 'FTResult']).size().reset_index(name='Count')
df_q5['Percentage'] = df_q5.groupby('Division')['Count'].transform(lambda x: x / x.sum() * 100)

result_names = {'H': 'Home Win', 'D': 'Draw', 'A': 'Away Win'}
df_q5['FTResult'] = df_q5['FTResult'].map(result_names)

fig_q5 = px.bar(
    data_frame=df_q5,
    x='Division',
    y='Percentage',
    hover_name='Division',
    color='FTResult',
    barmode='group',
    title="Match Result Distribution by League (Home / Draw / Away)",
    labels={"Division": "League", "Percentage": "Share of Matches (%)", "FTResult": "Result"},
    color_discrete_sequence=px.colors.qualitative.Safe,
    text_auto='.1f'
)
fig_q5.update_layout(
    width=1000,
    height=550,
    legend_title_text='Result'
)
fig_q5.update_xaxes(
    title="League"
)
fig_q5.update_yaxes(
    title="Share of Matches (%)",
    gridcolor='lightgrey'
)
fig_q5.update_traces(
    textposition='outside'
)

# Figure 6.1
df_q6 = filtered[['Season', 'FTResult']].dropna()
df_q6['IsHomeWin'] = (df_q6['FTResult'] == 'H').astype(int)
df_q6 = df_q6.groupby('Season')['IsHomeWin'].mean().reset_index()
df_q6.columns = ['Season', 'Percentage']
df_q6['Percentage'] = df_q6['Percentage'] * 100

fig_q6a = px.line(
    data_frame=df_q6,
    x="Season",
    y="Percentage",
    markers=True,
    title="Percentage of home wins per season",
    height=500
)
fig_q6a.update_layout(
    width=1200,
    legend_title_text=' '
)
fig_q6a.update_xaxes(
    title="Season",
    tickangle=45,
    categoryorder='array',
    categoryarray=sorted(df_q6['Season'].unique())
)
fig_q6a.update_yaxes(
    title="Percentage of home wins",
    gridcolor='lightgrey'
)

# Figure 6.2
df_q6b = filtered[['Division', 'Season', 'FTResult']].dropna()
df_q6b = df_q6b.groupby(['Division', 'Season', 'FTResult']).size().reset_index(name='Count')
df_q6b['Percentage'] = df_q6b.groupby(['Division', 'Season'])['Count'].transform(lambda x: x / x.sum() * 100)
df_q6b = df_q6b.loc[df_q6b['FTResult'] == 'H', :]
result_names = {'H': 'Home Win'}
df_q6b['FTResult'] = df_q6b['FTResult'].map(result_names)

fig_q6b = px.line(
    data_frame=df_q6b,
    x="Season",
    y="Percentage",
    hover_name='Division',
    color='Division',
    color_discrete_sequence=px.colors.qualitative.Safe,
    markers=True,
    title="Percentage of home wins per season",
    height=500
)
fig_q6b.update_layout(
    width=1200,
    legend_title_text=' '
)
fig_q6b.update_xaxes(
    title="Season",
    tickangle=45,
    categoryorder='array',
    categoryarray=sorted(df_q6b['Season'].unique())
)
fig_q6b.update_yaxes(
    title="Percentage of home wins",
    gridcolor='lightgrey'
)

# Figure 7
df_q7 = matches.loc[matches['Division'].isin(top5_leagues), :]
df_q7 = df_q7[['HomeTeam',  'FTResult']].dropna()
df_q7 = df_q7.groupby(['HomeTeam', 'FTResult']).size().reset_index(name='Count')
# in percent
df_q7['Percentage'] = df_q7.groupby(['HomeTeam'])['Count'].transform(lambda x: x / x.sum() * 100)
df_q7 = df_q7.loc[df_q7['FTResult'] == 'H', :]
result_names = {'H': 'Home Win'}
df_q7['FTResult'] = df_q7['FTResult'].map(result_names)

top5_teams = df_q7.sort_values('Percentage', ascending=False).head(5)['HomeTeam'].tolist()
df_q7 = matches[['Season', 'HomeTeam',  'FTResult']].dropna()
df_q7 = df_q7[df_q7['HomeTeam'].isin(top5_teams)]
df_q7 = df_q7.groupby(['Season', 'HomeTeam', 'FTResult']).size().reset_index(name='Count')
# in percent
df_q7['Percentage'] = df_q7.groupby(['Season', 'HomeTeam'])['Count'].transform(lambda x: x / x.sum() * 100)
df_q7 = df_q7.loc[df_q7['FTResult'] == 'H', :]
result_names = {'H': 'Home Win'}
df_q7['FTResult'] = df_q7['FTResult'].map(result_names)

fig_q7 = px.line(
    data_frame=df_q7,
    x="Season",
    y="Percentage",
    color= 'HomeTeam',
    hover_name='HomeTeam',
    color_discrete_sequence=px.colors.qualitative.Safe,
    markers=True, # to turn markers on - default is off
    title="Percentage of home wins per season (top 5 clubs with the highest winrate)",
    height=500
    )


fig_q7.update_layout(
    width=1200,
    legend_title_text=' '
    )

fig_q7.update_xaxes(
    title="Season",
    tickangle=45,
    categoryorder='array',
    categoryarray=sorted(df_q2['Season'].unique())
    )

fig_q7.update_yaxes(
    title="Percentage of home wins",
    gridcolor='lightgrey'
    )

#Figure 8
df_q8 = matches.loc[(matches['Division'] == 'Germany Bundesliga') & (matches['Season'] == '2019/20'), :]
df_q8 = df_q8[['MatchDateTime', 'HomeTeam', 'FTResult']].dropna()

covid_start = pd.Timestamp('2020-03-11')
df_q8['Period'] = df_q8['MatchDateTime'].apply(lambda x: 'Post-COVID (No Spectators)' if x >= covid_start else 'Pre-COVID (With Spectators)')
df_q8['IsHomeWin'] = (df_q8['FTResult'] == 'H').astype(int)

df_q8 = df_q8.groupby(['HomeTeam', 'Period'])['IsHomeWin'].mean().reset_index()
df_q8.columns = ['Team', 'Period', 'Home Win Rate']

fig_q8 = px.bar(
    data_frame=df_q8,
    x='Team',
    y='Home Win Rate',
    color='Period',
    hover_name='Team',
    barmode='group',
    title="Home Win Rate by Bundesliga Club — Before vs. After COVID (No Spectators)",
    labels={"Team": "Club", "Home Win Rate": "Home Win Rate", "Period": "Period"},
    color_discrete_sequence=px.colors.qualitative.Safe
)
fig_q8.update_layout(
    width=1300,
    height=600,
    legend_title_text='Period'
)
fig_q8.update_xaxes(
    title="Club",
    tickangle=45,
    categoryorder='total descending'
)
fig_q8.update_yaxes(
    title="Home Win Rate",
    tickformat=".0%",
    gridcolor='lightgrey'
)


df_q8b = df_q8.pivot(index='Team', columns='Period', values='Home Win Rate').reset_index()
df_q8b['Difference'] = df_q8b['Post-COVID (No Spectators)'] - df_q8b['Pre-COVID (With Spectators)']
df_q8b = df_q8b.sort_values('Difference', ascending=False)

fig_q8b = px.bar(
    data_frame=df_q8b,
    x='Team',
    y='Difference',
    color='Difference',
    hover_name='Team',
    color_continuous_scale=['#D55E00', 'lightgrey', '#0072B2'],    color_continuous_midpoint=0,
    title="Change in Home Win Rate — Bundesliga Clubs (Post-COVID vs. Pre-COVID)",
    labels={"Team": "Club", "Difference": "Change in Home Win Rate"}
)

fig_q8b.update_layout(
    width=1300,
    height=600,
    coloraxis_showscale=False
)
fig_q8b.update_xaxes(
    title="Club",
    tickangle=45,
    categoryorder='total descending'
)
fig_q8b.update_yaxes(
    title="Change in Home Win Rate",
    tickformat=".0%",
)


#Figure 9
df_q9 = matches[matches['Division'].isin(top5_leagues)][['Season', 'HomeElo', 'AwayElo', 'FTResult']].dropna()
df_q9['EloDifference'] = df_q9['HomeElo'] - df_q9['AwayElo']
df_q9['HomeWin'] = (df_q9['FTResult'] == 'H').astype(int)

# Elo difference in 50 bins
df_q9['EloBin'] = (df_q9['EloDifference'] // 50) * 50

# mean and count of games per bin
df_q9 = df_q9.groupby(['Season', 'EloBin'])['HomeWin'].agg(['mean', 'count']).reset_index()
df_q9.columns = ['Season', 'Elo Difference', 'Win Probability', 'Match Count']

# Bins with not enough games
df_q9 = df_q9[df_q9['Match Count'] >= 5]

fig_q9 = px.scatter(
    data_frame=df_q9,
    x='Elo Difference',
    y='Win Probability',
    animation_frame='Season',
    hover_name='Season',
    trendline='ols',
    title="Elo Difference vs. Home Win Probability Over Time (top 5 leagues, at least 5 matches per bin)",
    labels={"Elo Difference": "Elo Difference (Home − Away)", "Win Probability": "Home Win Probability"},
    color_discrete_sequence=px.colors.qualitative.Safe,
    range_x=[df_q9['Elo Difference'].min(), df_q9['Elo Difference'].max()],
    range_y=[0, 1]
)

fig_q9.update_layout(
    width=900,
    height=600
)
fig_q9.update_xaxes(
    title="Elo Difference (Home − Away)",
    gridcolor='lightgrey'
)
fig_q9.update_yaxes(
    title="Home Win Probability",
    tickformat=".0%",
    gridcolor='lightgrey'
)
fig_q9.update_traces(
    marker=dict(size=8)
)


# Figure 10
df_q10 = filtered[['Season', 'TotalYellow', 'TotalRed']].dropna()
df_q10 = df_q10.groupby('Season')[['TotalYellow', 'TotalRed']].mean().reset_index()
df_q10.columns = ['Season', 'Avg Yellow Cards', 'Avg Red Cards']

from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig_q10 = make_subplots(specs=[[{"secondary_y": True}]])
fig_q10.add_trace(
    go.Scatter(x=df_q10['Season'], y=df_q10['Avg Yellow Cards'], 
               mode='lines+markers', name='Yellow Cards',
               line=dict(color='gold'),
               hovertemplate='<b>Yellow Cards</b><br>Season: %{x}<br>Average: %{y:.2f}<extra></extra>'),
    secondary_y=False
)
fig_q10.add_trace(
    go.Scatter(x=df_q10['Season'], y=df_q10['Avg Red Cards'], 
               mode='lines+markers', name='Red Cards',
               line=dict(color='red'),
               hovertemplate='<b>Red Cards</b><br>Season: %{x}<br>Average: %{y:.2f}<extra></extra>'),
    secondary_y=True
)
fig_q10.update_layout(
    title="Average Number of Yellow/Red Cards per Match Over Time",
    width=1200,
    height=600,
    legend_title_text='Card Type'
)
fig_q10.update_xaxes(
    title="Season",
    tickangle=45,
    categoryorder='array',
    categoryarray=sorted(df_q10['Season'].unique())
)
fig_q10.update_yaxes(title_text="Average Yellow Cards per Match", secondary_y=False, gridcolor='lightgrey')
fig_q10.update_yaxes(title_text="Average Red Cards per Match", secondary_y=True)


# Figure 11
df_q11 = filtered[['Division', 'Season', 'TotalGoals']].dropna()
df_q11['Over25'] = (df_q11['TotalGoals'] > 2.5).astype(int)
df_q11 = df_q11.groupby(['Division', 'Season'])['Over25'].mean().reset_index()
df_q11.columns = ['Division', 'Season', 'Over 2.5 Goals Ratio']

df_q11_pivot = df_q11.pivot(index='Division', columns='Season', values='Over 2.5 Goals Ratio')
df_q11_pivot = df_q11_pivot[sorted(df_q11_pivot.columns)]

fig_q11 = px.imshow(
    df_q11_pivot,
    title="Share of Matches with Over 2.5 Goals — by League and Season",
    labels=dict(x="Season", y="League", color="Over 2.5 Goals Ratio"),
    color_continuous_scale='Blues',
    aspect='auto'
)
fig_q11.update_layout(
    width=1400,
    height=500
)
fig_q11.update_xaxes(
    tickangle=45
)
fig_q11.update_coloraxes(
    colorbar_tickformat='.0%'
)






st.header("How does the average number of goals per match differ across leagues?")
st.plotly_chart(fig_q1a, use_container_width=True)
st.header("How has the average number of goals per season changed over the years (2000–2025)?")
st.plotly_chart(fig_q2, use_container_width=True)
st.header("How has the average number of shots on target evolved over time — is there a trend toward more offensive football?")
st.plotly_chart(fig_q3, use_container_width=True)
st.header("Does kickoff time affect the number of goals scored?")
st.plotly_chart(fig_q4a, use_container_width=True)
st.header("Is there a home advantage, and is it stronger in some leagues than others?")
st.plotly_chart(fig_q5, use_container_width=True)
st.header("Has home advantage changed over the 25 years?")
st.plotly_chart(fig_q6a, use_container_width=True)
st.plotly_chart(fig_q6b, use_container_width=True)
st.header("Which teams show the most consistent home advantage over time (top 5 clubs by home win %, in top 5 leagues)?")
st.plotly_chart(fig_q7, use_container_width=True)
st.header("Is there a COVID effect (matches without spectators) visible in home advantage for Bundesliga Clubs?")
st.plotly_chart(fig_q8, use_container_width=True)
st.plotly_chart(fig_q8b, use_container_width=True)
st.header("Does the Elo difference correlate with win probability, and has this correlation changed over the years (top 5 leagues)?")
st.plotly_chart(fig_q9, use_container_width=True)
st.header("How has the average number of yellow/red cards evolved per year?")
st.plotly_chart(fig_q10, use_container_width=True)
st.header("How is the over/under 2.5 goals ratio distributed by league and year?")
st.plotly_chart(fig_q11, use_container_width=True)



col1, col2 = st.columns(2)

#col1.plotly_chart(fig_q1a)
#col1.plotly_chart(fig_q2)

