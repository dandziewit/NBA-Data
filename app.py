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
    Returns tuple of (players_df, team_stats_df)
    """
    fetcher = NBADataFetcher()
    
    with st.spinner("Fetching NBA data from API..."):
        # Fetch player data
        players_df = fetcher.get_complete_player_data()
        
        # Debug: Print detailed column information
        if not players_df.empty:
            print("\n" + "="*60)
            print("=== RAW PLAYER DATA ===" )
            print("="*60)
            print(f"Total players: {len(players_df)}")
            print(f"All columns: {players_df.columns.tolist()}")
            print(f"Column dtypes: {players_df.dtypes.to_dict()}")
            
            # Check for team column variations
            team_cols = [col for col in players_df.columns if 'team' in col.lower()]
            print(f"Team-related columns found: {team_cols}")
            
            # Ensure team column exists and is properly formatted
            if "team" in players_df.columns:
                print(f"✓ 'team' column exists")
                print(f"  Data type: {players_df['team'].dtype}")
                print(f"  Sample raw values: {players_df['team'].head(10).tolist()}")
                
                # Store original team data before any conversion
                original_team = players_df["team"].copy()
                
                # Clean and convert to string, preserving actual team names
                players_df["team"] = players_df["team"].fillna("Unknown").astype(str).str.strip()
                
                # Verify conversion didn't introduce numeric issues
                print(f"  After cleanup: {players_df['team'].head(10).tolist()}")
                print(f"  Unique teams: {sorted(players_df['team'].unique().tolist())}")
                print(f"  Missing/Unknown: {(players_df['team'] == 'Unknown').sum()}")
                
            elif team_cols:
                # Try to use alternative team column
                alt_col = team_cols[0]
                print(f"⚠ 'team' column not found, using '{alt_col}' instead")
                players_df["team"] = players_df[alt_col].fillna("Unknown").astype(str).str.strip()
                print(f"  Sample values: {players_df['team'].head(10).tolist()}")
            else:
                # No team column found at all
                print("❌ No team-related column found! Creating default 'Unknown' values")
                players_df["team"] = "Unknown"
            
            print("="*60)
        
        # Fetch team stats
        team_stats_df = fetcher.fetch_team_stats()
    
    return players_df, team_stats_df

def format_player_name(row):
    """Format player name from DataFrame row"""
    try:
        first = row.get('first_name', '') if hasattr(row, 'get') else ''
        last = row.get('last_name', '') if hasattr(row, 'get') else ''
        return f"{first} {last}".strip() or "Unknown"
    except:
        return "Unknown"

def format_team_name(row):
    """Format team name from DataFrame row"""
    try:
        # Access team directly from pandas Series using bracket notation
        team = row["team"] if "team" in row.index else None
        
        # Check if team exists and is not null/empty
        if team is not None and pd.notna(team):
            team_str = str(team).strip()
            if team_str and team_str != "" and team_str.lower() != "nan":
                return team_str
        
        return "Unknown"
    except Exception as e:
        return "Unknown"

def display_player_rankings(players_df, calculator, projector):
    """Display player rankings section"""
    st.markdown('<p class="sub-header">🏆 Top Players Rankings</p>', unsafe_allow_html=True)
    
    # Debug initial state
    print("\n=== DISPLAY_PLAYER_RANKINGS START ===")
    print(f"Input DataFrame columns: {players_df.columns.tolist()}")
    print(f"Has 'team' column: {'team' in players_df.columns}")
    
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
    print("\n[After calculate_player_efficiency]")
    print(f"  Has 'team': {'team' in players_with_efficiency.columns}")
    if "team" in players_with_efficiency.columns:
        print(f"  Type: {players_with_efficiency['team'].dtype}")
        print(f"  Sample: {players_with_efficiency['team'].head(5).tolist()}")
        # Check if team got overwritten with numbers
        if players_with_efficiency['team'].dtype in ['int64', 'float64']:
            print("  ❌ ERROR: team column is numeric! It was overwritten!")
    
    # Filter by games played if column exists
    if "games_played" in players_with_efficiency.columns:
        players_with_efficiency = players_with_efficiency[
            players_with_efficiency["games_played"] >= min_games
        ]
    
    # Add projections
    players_with_projections = projector.project_player_season_stats(players_with_efficiency)
    print("\n[After project_player_season_stats]")
    print(f"  Has 'team': {'team' in players_with_projections.columns}")
    if "team" in players_with_projections.columns:
        print(f"  Type: {players_with_projections['team'].dtype}")
        print(f"  Sample: {players_with_projections['team'].head(5).tolist()}")
    
    players_with_projections = projector.calculate_mvp_score(players_with_projections)
    print("\n[After calculate_mvp_score]")
    print(f"  Has 'team': {'team' in players_with_projections.columns}")
    if "team" in players_with_projections.columns:
        print(f"  Type: {players_with_projections['team'].dtype}")
        print(f"  Sample: {players_with_projections['team'].head(5).tolist()}")
    
    # Get top players
    top_players = calculator.rank_players(players_with_projections, top_n=top_n_players)
    print("\n[After rank_players]")
    print(f"  Has 'team': {'team' in top_players.columns}")
    if "team" in top_players.columns:
        print(f"  Type: {top_players['team'].dtype}")
        print(f"  Sample teams: {top_players['team'].head(10).tolist()}")
        print(f"  Unique teams: {top_players['team'].nunique()}")
        # Final check for numeric overwriting
        if top_players['team'].dtype in ['int64', 'float64']:
            print("  ❌ CRITICAL ERROR: team column contains numbers, not team names!")
        else:
            print("  ✓ team column contains strings")
    
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
        
        # Debug: Verify team column before display processing
        print("\n[Before creating display table]")
        print(f"  Columns: {display_df.columns.tolist()}")
        print(f"  Has 'team': {'team' in display_df.columns}")
        if "team" in display_df.columns:
            print(f"  Team type: {display_df['team'].dtype}")
            print(f"  Team sample: {display_df['team'].head(5).tolist()}")
        
        # Check if team column exists and show warning if not
        if "team" not in display_df.columns:
            st.warning("⚠️ Team column missing from data. Showing 'Unknown' for all teams.")
            display_df["team"] = "Unknown"
        
        # Format player and team names
        display_df["Player"] = display_df.apply(format_player_name, axis=1)
        
        # Create Team_Display column from the team column (not overwriting it)
        display_df["Team_Display"] = display_df.apply(format_team_name, axis=1)
        
        # Verify Team_Display was created correctly
        print(f"\n[After formatting]")
        print(f"  Team_Display sample: {display_df['Team_Display'].head(10).tolist()}")
        print(f"  Unique Team_Display values: {display_df['Team_Display'].nunique()}")
        
        # Add shooting stats columns if available
        display_columns = ["rank", "Player", "Team_Display", "pts", "reb", "ast", "stl", "blk"]
        
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
        col_names = ["Rank", "Player", "Team", "PTS", "REB", "AST", "STL", "BLK"]
        
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
        top_15["Team"] = top_15["team"] if "team" in top_15.columns else "N/A"
        
        fig = px.bar(
            top_15,
            x="efficiency",
            y="Player",
            orientation="h",
            title=f"Top 15 Players by Efficiency Rating",
            labels={"efficiency": "Efficiency Rating", "Player": ""},
            color="efficiency",
            color_continuous_scale="Blues",
            hover_data={"Team": True, "efficiency": ":.2f"} if "team" in top_15.columns else None
        )
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Stats comparison for top 10
        col1, col2 = st.columns(2)
        
        with col1:
            top_10 = top_players.head(10).copy()
            top_10["Player"] = top_10.apply(format_player_name, axis=1)
            
            fig2 = go.Figure()
            if "team" in top_10.columns:
                fig2.add_trace(go.Bar(name="PTS", x=top_10["Player"], y=top_10["pts"], 
                                      customdata=top_10["team"],
                                      hovertemplate='<b>%{x}</b><br>PTS: %{y}<br>Team: %{customdata}<extra></extra>'))
                fig2.add_trace(go.Bar(name="REB", x=top_10["Player"], y=top_10["reb"],
                                      customdata=top_10["team"],
                                      hovertemplate='<b>%{x}</b><br>REB: %{y}<br>Team: %{customdata}<extra></extra>'))
                fig2.add_trace(go.Bar(name="AST", x=top_10["Player"], y=top_10["ast"],
                                      customdata=top_10["team"],
                                      hovertemplate='<b>%{x}</b><br>AST: %{y}<br>Team: %{customdata}<extra></extra>'))
            else:
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
            if "team" in top_30.columns:
                hover_cols.append("team")
            
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

def display_team_standings(team_stats_df, calculator, projector):
    """Display team standings section"""
    st.markdown('<p class="sub-header">🏀 Team Standings & Rankings</p>', unsafe_allow_html=True)
    
    if team_stats_df.empty:
        st.warning("No team data available for the 2025-2026 season yet.")
        return
    
    # Calculate standings and projections
    standings_df = calculator.calculate_team_standings(team_stats_df)
    projected_df = projector.project_team_season_record(standings_df)
    playoff_df = projector.get_playoff_probability(projected_df)
    
    # Get conference standings
    east_df, west_df = calculator.get_conference_standings(team_stats_df)
    
    # Sidebar filter
    with st.sidebar:
        st.markdown("### Team Filters")
        conference_filter = st.radio("Conference", ["All", "Eastern", "Western"], index=0)
    
    # Overall metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Teams", len(standings_df))
    
    with col2:
        if not standings_df.empty:
            top_team = standings_df.iloc[0]
            st.metric("Best Record", f"{top_team['team_name']}: {top_team['wins']}-{top_team['losses']}")
    
    with col3:
        if not standings_df.empty:
            highest_ppg = standings_df.nlargest(1, "ppg").iloc[0]
            st.metric("Highest Scoring", f"{highest_ppg['team_name']}: {highest_ppg['ppg']:.1f} PPG")
    
    with col4:
        if not standings_df.empty:
            best_diff = standings_df.nlargest(1, "point_differential").iloc[0]
            st.metric("Best Point Diff", f"{best_diff['team_name']}: +{best_diff['point_differential']:.1f}")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Overall Standings", "🌐 Conference Standings", 
                                       "📈 Team Stats", "🎯 Projections"])
    
    with tab1:
        # Filter by conference
        if conference_filter == "Eastern":
            display_standings = standings_df[standings_df["conference"] == "East"]
        elif conference_filter == "Western":
            display_standings = standings_df[standings_df["conference"] == "West"]
        else:
            display_standings = standings_df
        
        # Prepare display
        display_cols = ["overall_rank", "team_name", "conference", "wins", "losses", 
                       "win_pct", "point_differential", "ppg", "opp_ppg"]
        display_cols = [col for col in display_cols if col in display_standings.columns]
        
        display_df = display_standings[display_cols].copy()
        display_df.columns = ["Rank", "Team", "Conf", "W", "L", "Win%", 
                             "Diff", "PPG", "Opp PPG"]
        display_df["Win%"] = (display_df["Win%"] * 100).round(1)
        
        st.dataframe(display_df, hide_index=True, use_container_width=True, height=600)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Eastern Conference")
            if not east_df.empty:
                east_display = east_df[[
                    "conf_rank", "team_name", "wins", "losses", "win_pct", "point_differential"
                ]].copy()
                east_display.columns = ["Rank", "Team", "W", "L", "Win%", "Diff"]
                east_display["Win%"] = (east_display["Win%"] * 100).round(1)
                st.dataframe(east_display, hide_index=True, use_container_width=True)
            else:
                st.info("No Eastern Conference data available yet.")
        
        with col2:
            st.markdown("#### Western Conference")
            if not west_df.empty:
                west_display = west_df[[
                    "conf_rank", "team_name", "wins", "losses", "win_pct", "point_differential"
                ]].copy()
                west_display.columns = ["Rank", "Team", "W", "L", "Win%", "Diff"]
                west_display["Win%"] = (west_display["Win%"] * 100).round(1)
                st.dataframe(west_display, hide_index=True, use_container_width=True)
            else:
                st.info("No Western Conference data available yet.")
    
    with tab3:
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                standings_df.head(15),
                x="team_name",
                y="wins",
                title="Top 15 Teams by Wins",
                labels={"wins": "Wins", "team_name": "Team"},
                color="wins",
                color_continuous_scale="Greens"
            )
            fig.update_layout(height=400, xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig2 = px.scatter(
                standings_df,
                x="ppg",
                y="point_differential",
                size="wins",
                hover_data=["team_name"],
                title="Points Per Game vs Point Differential",
                labels={"ppg": "Points Per Game", "point_differential": "Point Differential"}
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Point differential chart
        fig3 = px.bar(
            standings_df.head(20),
            x="team_name",
            y="point_differential",
            title="Point Differential - Top 20 Teams",
            labels={"point_differential": "Point Differential", "team_name": "Team"},
            color="point_differential",
            color_continuous_scale="RdYlGn"
        )
        fig3.update_layout(height=400, xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
    
    with tab4:
        if "projected_total_wins" in playoff_df.columns:
            st.markdown("#### Season Projections & Playoff Outlook")
            
            proj_display = playoff_df[[
                "team_name", "conference", "wins", "losses",
                "projected_total_wins", "projected_total_losses",
                "playoff_probability", "conf_rank"
            ]].copy()
            
            proj_display.columns = [
                "Team", "Conf", "Current W", "Current L",
                "Proj. W", "Proj. L", "Playoff %", "Conf Rank"
            ]
            
            proj_display = proj_display.sort_values(["Conf", "Playoff %"], ascending=[True, False])
            
            st.dataframe(proj_display, hide_index=True, use_container_width=True, height=600)
            
            # Playoff probability visualization
            playoff_teams = playoff_df[playoff_df["playoff_probability"] >= 50].sort_values(
                "playoff_probability", ascending=False
            )
            
            if not playoff_teams.empty:
                fig = px.bar(
                    playoff_teams,
                    x="team_name",
                    y="playoff_probability",
                    color="conference",
                    title="Teams with 50%+ Playoff Probability",
                    labels={"playoff_probability": "Playoff Probability (%)", "team_name": "Team"},
                    color_discrete_map={"East": "#1E3A8A", "West": "#DC2626"}
                )
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Projection data will be available once more games are played.")

def main():
    """Main application function"""
    
    # Load data first to detect season
    try:
        players_df, team_stats_df = load_nba_data()
        
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
    
    # Create main tabs
    main_tab1, main_tab2 = st.tabs(["👤 Player Analysis", "🏆 Team Analysis"])
    
    with main_tab1:
        display_player_rankings(players_df, calculator, projector)
    
    with main_tab2:
        display_team_standings(team_stats_df, calculator, projector)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Data source: [balldontlie.io](https://www.balldontlie.io) | "
        "Built with Streamlit | Last updated: " + time.strftime("%Y-%m-%d %H:%M:%S")
    )

if __name__ == "__main__":
    main()
