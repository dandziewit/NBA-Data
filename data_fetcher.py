"""
NBA Data Fetcher Module
Handles all data fetching from nba_api (stats.nba.com)
"""

import pandas as pd
from nba_api.stats.endpoints import leagueleaders, teamestimatedmetrics, leaguestandings
from nba_api.stats.static import teams
import time
from typing import Dict, List, Optional

class NBADataFetcher:
    """
    Class for fetching NBA data from nba_api (stats.nba.com)
    """
    
    def __init__(self):
        """Initialize the NBA Data Fetcher"""
        # Current season (2025-26 season)
        self.current_season = "2025-26"
        self.season_year = "2025-26"
        
    def fetch_all_teams(self) -> pd.DataFrame:
        """
        Fetch all NBA teams
        
        Returns:
            DataFrame containing team information
        """
        print("Fetching all NBA teams...")
        
        try:
            all_teams = teams.get_teams()
            df = pd.DataFrame(all_teams)
            print(f"Fetched {len(df)} teams")
            return df
        except Exception as e:
            print(f"Error fetching teams: {e}")
            return pd.DataFrame()
    
    def fetch_player_stats(self) -> pd.DataFrame:
        """
        Fetch player statistics for current season
        
        Returns:
            DataFrame containing player stats
        """
        print(f"Fetching player stats for {self.current_season} season...")
        
        try:
            # Get league leaders (top performers with full stats)
            leaders = leagueleaders.LeagueLeaders(
                season=self.current_season,
                season_type_all_star='Regular Season',
                per_mode48='PerGame',
                stat_category_abbreviation='PTS'
            )
            
            time.sleep(1)  # Rate limiting
            
            df = leaders.get_data_frames()[0]
            
            if df.empty:
                print("No player data available for current season")
                return pd.DataFrame()
            
            print(f"Fetched stats for {len(df)} players")
            
            # Rename columns to match our expected format
            column_mapping = {
                'PLAYER_ID': 'id',
                'PLAYER': 'player_name',
                'TEAM_ABBREVIATION': 'team',
                'GP': 'games_played',
                'MIN': 'min',
                'PTS': 'pts',
                'REB': 'reb',
                'AST': 'ast',
                'STL': 'stl',
                'BLK': 'blk',
                'FG_PCT': 'fg_pct',
                'FG3_PCT': 'fg3_pct',
                'FT_PCT': 'ft_pct',
                'TOV': 'turnover'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Split player name into first and last
            if 'player_name' in df.columns:
                df[['first_name', 'last_name']] = df['player_name'].str.split(' ', n=1, expand=True)
            
            return df
            
        except Exception as e:
            print(f"Error fetching player stats: {e}")
            print("Trying fallback season 2024-25...")
            
            try:
                # Try previous season as fallback
                leaders = leagueleaders.LeagueLeaders(
                    season="2024-25",
                    season_type_all_star='Regular Season',
                    per_mode48='PerGame'
                )
                
                time.sleep(1)
                df = leaders.get_data_frames()[0]
                
                if not df.empty:
                    self.current_season = "2024-25"
                    print(f"Using 2024-25 season data: {len(df)} players")
                    
                    # Apply same column mapping
                    column_mapping = {
                        'PLAYER_ID': 'id',
                        'PLAYER': 'player_name',
                        'TEAM_ABBREVIATION': 'team',
                        'GP': 'games_played',
                        'MIN': 'min',
                        'PTS': 'pts',
                        'REB': 'reb',
                        'AST': 'ast',
                        'STL': 'stl',
                        'BLK': 'blk',
                        'FG_PCT': 'fg_pct',
                        'FG3_PCT': 'fg3_pct',
                        'FT_PCT': 'ft_pct',
                        'TOV': 'turnover'
                    }
                    
                    df = df.rename(columns=column_mapping)
                    
                    if 'player_name' in df.columns:
                        df[['first_name', 'last_name']] = df['player_name'].str.split(' ', n=1, expand=True)
                    
                    return df
                
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                
            return pd.DataFrame()
    
    def fetch_team_stats(self) -> pd.DataFrame:
        """
        Fetch team standings and statistics
        
        Returns:
            DataFrame containing team statistics
        """
        print(f"Fetching team stats for {self.current_season} season...")
        
        try:
            # Get league standings
            standings = leaguestandings.LeagueStandings(
                season=self.current_season,
                season_type='Regular Season'
            )
            
            time.sleep(1)  # Rate limiting
            
            df = standings.get_data_frames()[0]
            
            if df.empty:
                print("No team standings available")
                return pd.DataFrame()
            
            print(f"Fetched standings for {len(df)} teams")
            
            # Rename columns to match our expected format
            column_mapping = {
                'TeamID': 'team_id',
                'TeamCity': 'team_city',
                'TeamName': 'team_name_short',
                'Conference': 'conference',
                'WINS': 'wins',
                'LOSSES': 'losses',
                'WinPCT': 'win_pct',
                'ConferenceRecord': 'conf_record',
                'HOME': 'home_record',
                'ROAD': 'road_record'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Create full team name
            if 'team_city' in df.columns and 'team_name_short' in df.columns:
                df['team_name'] = df['team_city'] + ' ' + df['team_name_short']
            
            # Calculate games played
            if 'wins' in df.columns and 'losses' in df.columns:
                df['games_played'] = df['wins'] + df['losses']
            
            # Add placeholder stats (we'll calculate from wins/losses)
            if 'games_played' in df.columns and df['games_played'].sum() > 0:
                # Estimate points based on league averages (roughly 110-115 ppg)
                df['points_for'] = df['wins'] * 115 + df['losses'] * 105
                df['points_against'] = df['wins'] * 105 + df['losses'] * 115
                df['point_differential'] = df['points_for'] - df['points_against']
                df['ppg'] = df['points_for'] / df['games_played']
                df['opp_ppg'] = df['points_against'] / df['games_played']
            
            return df
            
        except Exception as e:
            print(f"Error fetching team stats: {e}")
            return pd.DataFrame()
    
    def get_complete_player_data(self) -> pd.DataFrame:
        """
        Fetch complete player data
        
        Returns:
            DataFrame with player stats
        """
        return self.fetch_player_stats()

