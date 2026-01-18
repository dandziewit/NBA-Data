"""
NBA Analyzer Streamlit App
Interactive GUI for analyzing NBA 2025-2026 season data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_fetcher import NBADataFetcher
from stats_calculator import NBAStatsCalculator
from projections import NBAProjections
import time

# Page configuration
st.set_page_config(
    page_title="NBA 2025-2026 Analyzer",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3B82F6;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_nba_data():
    """
    Load NBA data from API with caching
    Returns players_df
    """
    fetcher = NBADataFetcher()
    
    with st.spinner("Fetching NBA data from API..."):
        # Fetch player data
        players_df = fetcher.get_complete_player_data()
        
        if not players_df.empty:
            print(f"\nFetched {len(players_df)} players with {len(players_df.columns)} columns")
    
    return players_df

def format_player_name(row):
    """Format player name from DataFrame row"""
    try:
        first = row.get('first_name', '') if hasattr(row, 'get') else ''
        last = row.get('last_name', '') if hasattr(row, 'get') else ''
        return f"{first} {last}".strip() or "Unknown"
    except:
        return "Unknown"

def display_player_rankings(players_df, calculator, projector):
    """Display player rankings section"""
    st.markdown('<p class="sub-header">🏆 Top Players Rankings</p>', unsafe_allow_html=True)
    
    # Check if we have any data at all
    if players_df.empty:
        st.warning("No player data available for the 2025-2026 season yet.")
        st.info("💡 Tip: The NBA API updates as games are played. Check back during the regular season!")
        return
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("### Player Filters")
        top_n_players = st.slider("Number of players to display", 10, 100, 50, 5)
        min_games = st.slider("Minimum games played", 1, 30, 5)
    
    # Calculate efficiency and rankings
    players_with_efficiency = calculator.calculate_player_efficiency(players_df)
    
    # Filter by games played if column exists
    if "games_played" in players_with_efficiency.columns:
        players_with_efficiency = players_with_efficiency[
            players_with_efficiency["games_played"] >= min_games
        ]
    
    # Add projections
    players_with_projections = projector.project_player_season_stats(players_with_efficiency)
    players_with_projections = projector.calculate_mvp_score(players_with_projections)
    
    # Get top players
    top_players = calculator.rank_players(players_with_projections, top_n=top_n_players)
    
    if top_players.empty:
        st.warning("No player statistics available yet for the 2025-2026 season.")
        st.info("The API may not have season averages data yet. This data becomes available once games are played.")
        return
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players Analyzed", len(players_with_efficiency))
    
    with col2:
        top_scorer = players_with_efficiency.nlargest(1, "pts")
        if not top_scorer.empty:
            st.metric("Top Scorer (PPG)", 
                     f"{format_player_name(top_scorer.iloc[0])}: {top_scorer.iloc[0]['pts']:.1f}")
    
    with col3:
        top_rebounder = players_with_efficiency.nlargest(1, "reb")
        if not top_rebounder.empty:
            st.metric("Top Rebounder (RPG)", 
                     f"{format_player_name(top_rebounder.iloc[0])}: {top_rebounder.iloc[0]['reb']:.1f}")
    
    with col4:
        top_assister = players_with_efficiency.nlargest(1, "ast")
        if not top_assister.empty:
            st.metric("Top Playmaker (APG)", 
                     f"{format_player_name(top_assister.iloc[0])}: {top_assister.iloc[0]['ast']:.1f}")
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["📊 Rankings Table", "📈 Visualizations"])
    
    with tab1:
        # Prepare display dataframe
        display_df = top_players.copy()
        
        # Format player names
        display_df["Player"] = display_df.apply(format_player_name, axis=1)
        
        # Add shooting stats columns if available
        display_columns = ["rank", "Player", "pts", "reb", "ast", "stl", "blk"]
        
        # Add 3-point stats if available
        if "FG3M" in display_df.columns:
            display_columns.append("FG3M")
        if "FG3A" in display_df.columns:
            display_columns.append("FG3A")
        if "fg3_pct" in display_df.columns:
            display_columns.append("fg3_pct")
        
        # Add other stats
        display_columns.extend(["efficiency", "games_played", "min"])
        display_columns = [col for col in display_columns if col in display_df.columns]
        
        display_df = display_df[display_columns]
        
        # Rename columns for display
        col_names = ["Rank", "Player", "PTS", "REB", "AST", "STL", "BLK"]
        
        if "FG3M" in display_columns:
            col_names.append("3PM")
        if "FG3A" in display_columns:
            col_names.append("3PA")
        if "fg3_pct" in display_columns:
            col_names.append("3P%")
            
        col_names.extend(["Efficiency", "GP", "MIN"])
        
        display_df.columns = col_names[:len(display_df.columns)]
        
        # Format percentages
        if "3P%" in display_df.columns:
            display_df["3P%"] = (display_df["3P%"] * 100).round(1)
        
        # Style the dataframe
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True,
            height=600
        )
    
    with tab2:
        # Top 15 players efficiency bar chart
        top_15 = top_players.head(15).copy()
        top_15["Player"] = top_15.apply(format_player_name, axis=1)
        
        fig = px.bar(
            top_15,
            x="efficiency",
            y="Player",
            orientation="h",
            title=f"Top 15 Players by Efficiency Rating",
            labels={"efficiency": "Efficiency Rating", "Player": ""},
            color="efficiency",
            color_continuous_scale="Blues"
        )
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Stats comparison for top 10
        col1, col2 = st.columns(2)
        
        with col1:
            top_10 = top_players.head(10).copy()
            top_10["Player"] = top_10.apply(format_player_name, axis=1)
            
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(name="PTS", x=top_10["Player"], y=top_10["pts"]))
            fig2.add_trace(go.Bar(name="REB", x=top_10["Player"], y=top_10["reb"]))
            fig2.add_trace(go.Bar(name="AST", x=top_10["Player"], y=top_10["ast"]))
            
            fig2.update_layout(
                title="Top 10 Players: PTS, REB, AST Comparison",
                barmode="group",
                height=400,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            top_30 = top_players.head(30).copy()
            hover_cols = []
            if "first_name" in top_30.columns:
                hover_cols.append("first_name")
            if "last_name" in top_30.columns:
                hover_cols.append("last_name")
            
            fig3 = px.scatter(
                top_30,
                x="pts",
                y="efficiency",
                size="games_played" if "games_played" in top_30.columns else None,
                hover_data=hover_cols if hover_cols else None,
                title="Scoring vs Efficiency (Top 30 Players)",
                labels={"pts": "Points Per Game", "efficiency": "Efficiency Rating"}
            )
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)
        
        # Add 3-point shooting leaders section
        st.markdown("#### 🎯 Three-Point Shooting Leaders")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 3-point shooters by makes
            if "FG3M" in players_with_efficiency.columns:
                top_3pm = players_with_efficiency.nlargest(10, "FG3M").copy()
                top_3pm["Player"] = top_3pm.apply(format_player_name, axis=1)
                
                fig_3pm = px.bar(
                    top_3pm,
                    x="Player",
                    y="FG3M",
                    title="Top 10: Three-Pointers Made Per Game",
                    labels={"FG3M": "3-Pointers Made"},
                    color="FG3M",
                    color_continuous_scale="Greens"
                )
                fig_3pm.update_layout(height=400, xaxis_tickangle=-45, showlegend=False)
                st.plotly_chart(fig_3pm, use_container_width=True)
        
        with col2:
            # Top 3-point shooters by percentage (min 2 attempts)
            if "fg3_pct" in players_with_efficiency.columns and "FG3A" in players_with_efficiency.columns:
                top_3pct = players_with_efficiency[players_with_efficiency["FG3A"] >= 2.0].nlargest(10, "fg3_pct").copy()
                top_3pct["Player"] = top_3pct.apply(format_player_name, axis=1)
                top_3pct["3P%"] = (top_3pct["fg3_pct"] * 100).round(1)
                
                fig_3pct = px.bar(
                    top_3pct,
                    x="Player",
                    y="3P%",
                    title="Top 10: Three-Point Percentage (min 2 att/game)",
                    labels={"3P%": "Three-Point %"},
                    color="3P%",
                    color_continuous_scale="Blues"
                )
                fig_3pct.update_layout(height=400, xaxis_tickangle=-45, showlegend=False)
                st.plotly_chart(fig_3pct, use_container_width=True)

def main():
    """Main application function"""
    
    # Load data first to detect season
    try:
        players_df = load_nba_data()
        
        # Initialize calculators
        calculator = NBAStatsCalculator()
        projector = NBAProjections()
        
        # Get the detected season from data fetcher
        fetcher = NBADataFetcher()
        season_display = fetcher.current_season
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("This could be due to API rate limits or network issues. Please try again in a few moments.")
        
        with st.expander("Error Details"):
            st.exception(e)
        return
    
    # Header with detected season
    st.markdown(f'<p class="main-header">🏀 NBA {season_display} Season Analyzer</p>', unsafe_allow_html=True)
    st.markdown("### Live stats, rankings, and projections from balldontlie.io API")
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/0/03/National_Basketball_Association_logo.svg/1200px-National_Basketball_Association_logo.svg.png", 
                width=200)
        st.markdown("---")
        st.markdown("### About")
        st.info(
            f"This app analyzes the NBA {season_display} season using real-time data from the "
            "balldontlie.io API. Data is refreshed every hour."
        )
        st.markdown("---")
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Display player analysis
    display_player_rankings(players_df, calculator, projector)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Data source: [balldontlie.io](https://www.balldontlie.io) | "
        "Built with Streamlit | Last updated: " + time.strftime("%Y-%m-%d %H:%M:%S")
    )

if __name__ == "__main__":
    main()
