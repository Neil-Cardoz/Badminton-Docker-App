import streamlit as st
from mysql.connector import Error
import pandas as pd
import plotly.express as px
import time
import mysql.connector

import os


# DB Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "put_your_password_here",
    "database": "badminton_db"
}

# Dummy users (can replace with DB-based login)
users = {
    "admin": "admin123",
    "neil": "neilpass"
}

def save_team(team_name, player_names, match_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        for name in player_names:
            cursor.execute("INSERT INTO teams (match_id, team_name, player_name) VALUES (%s, %s, %s)",
                           (match_id, team_name, name))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        st.error(f"Error saving team: {e}")

def save_match(team_a, team_b, winner):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO matches (team_a, team_b, winner_team, created_at) VALUES (%s, %s, %s, NOW())",
                       (team_a, team_b, winner))
        match_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return match_id
    except Error as e:
        st.error(f"Error saving match: {e}")
        return None

def show_scoreboard():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql("SELECT player_name, wins, losses FROM player_stats", conn)
        conn.close()
        return df
    except Error as e:
        st.error(f"Error fetching scoreboard: {e}")
        return pd.DataFrame()

def fetch_win_percent_data():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql("SELECT * FROM player_stats_percent", conn)
        conn.close()
        return df
    except Error as e:
        st.error(f"Error fetching win percent data: {e}")
        return pd.DataFrame()

def fetch_wins_over_time():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        query = """
        SELECT 
            m.created_at,
            t.player_name,
            CASE WHEN m.winner_team = t.team_name THEN 1 ELSE 0 END AS win
        FROM matches m
        JOIN teams t ON m.match_id = t.match_id
        """
        df = pd.read_sql(query, conn)
        conn.close()

        df['date'] = pd.to_datetime(df['created_at']).dt.date
        win_summary = df[df['win'] == 1].groupby(['date', 'player_name']).size().reset_index(name='wins')
        return win_summary
    except Error as e:
        st.error(f"Error fetching wins over time: {e}")
        return pd.DataFrame()

def login_page():
    st.title("🏸 Badminton Tracker Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")

            # Scoreboard
            st.markdown("### 🏆 Player Scoreboard")
            scoreboard_data = show_scoreboard()
            if not scoreboard_data.empty:
                st.table(scoreboard_data)
            else:
                st.info("No match data available yet.")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Invalid credentials")

def team_form():
    st.title("🏸 Form Teams")
    with st.form("team_form"):
        st.markdown("### Team A")
        a1 = st.text_input("Team A - Player 1")
        a2 = st.text_input("Team A - Player 2")
        a3 = st.text_input("Team A - Player 3")

        st.markdown("### Team B")
        b1 = st.text_input("Team B - Player 1")
        b2 = st.text_input("Team B - Player 2")
        b3 = st.text_input("Team B - Player 3")

        winner = st.selectbox("Who Won?", ["Team A", "Team B"])

        submitted = st.form_submit_button("Submit Match")
        if submitted:
            team_a = [a1, a2, a3]
            team_b = [b1, b2, b3]
            match_id = save_match("Team A", "Team B", winner)
            if match_id:
                save_team("Team A", team_a, match_id)
                save_team("Team B", team_b, match_id)
                st.success("Match and teams saved!")

    st.markdown("---")
    st.markdown("### 📊 Analytics")
    win_df = fetch_win_percent_data()
    if not win_df.empty:
        st.markdown("#### 🏆 Win % by Player")
        fig = px.bar(win_df, x="player_name", y="win_percent", text="win_percent", color="player_name")
        st.plotly_chart(fig, use_container_width=True)

    line_df = fetch_wins_over_time()
    if not line_df.empty:
        st.markdown("#### 📈 Wins Over Time")
        fig2 = px.line(line_df, x="date", y="wins", color="player_name", markers=True)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Scoreboard
    st.markdown("### 🏆 Player Scoreboard")
    scoreboard_data = show_scoreboard()
    if not scoreboard_data.empty:
        st.table(scoreboard_data)

# Main App Logic
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    team_form()