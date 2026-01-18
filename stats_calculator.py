"""
NBA Stats Calculator Module
Calculates player and team rankings, efficiency metrics, and standings
"""

import pandas as pd
import numpy as np
from typing import Tuple

class NBAStatsCalculator:
    """
    Class for calculating NBA statistics, rankings, and standings
    """
    
    def __init__(self):
        """Initialize the stats calculator"""
        pass
    
    def calculate_player_efficiency(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate player efficiency rating
        Efficiency = (PTS + REB + AST + STL + BLK) / Games Played
        
        Args:
            players_df: DataFrame with player season averages
            
        Returns:
            DataFrame with efficiency rating added (all original columns preserved)
        """
        if players_df.empty:
            return players_df
        
        # Make a copy to avoid modifying original
        df = players_df.copy()
        
        # Debug: Verify team column exists and check type
        has_team = 'team' in df.columns
        team_backup = None  # Initialize backup
        print(f"[calculate_player_efficiency] Input has 'team': {has_team}")
        if has_team:
            team_backup = df['team'].copy()  # Backup team column
            print(f"  Input team type: {df['team'].dtype}")
            print(f"  Input team sample: {df['team'].head(3).tolist()}")
        
        # Ensure required columns exist with defaults
        for col in ["pts", "reb", "ast", "stl", "blk", "games_played"]:
            if col not in df.columns:
                df[col] = 0
        
        # Calculate efficiency (DO NOT assign to 'team' column)
        df["efficiency"] = (
            df["pts"].fillna(0) + 
            df["reb"].fillna(0) + 
            df["ast"].fillna(0) + 
            df["stl"].fillna(0) + 
            df["blk"].fillna(0)
        )
        
        # Filter out players with very few games (less than 5)
        df = df[df["games_played"].fillna(0) >= 5].copy()
        
        # Verify team column wasn't accidentally overwritten
        if has_team and team_backup is not None:
            if 'team' not in df.columns:
                print("  ❌ WARNING: team column was removed during processing! Restoring...")
                df['team'] = team_backup[df.index]
            elif df['team'].dtype != team_backup.dtype:
                print(f"  ❌ WARNING: team column type changed from {team_backup.dtype} to {df['team'].dtype}! Restoring...")
                df['team'] = team_backup[df.index]
            else:
                print(f"  ✓ team column preserved correctly")
                print(f"  Output team sample: {df['team'].head(3).tolist()}")
        
        return df
    
    def rank_players(self, players_df: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
        """
        Rank players by efficiency
        
        Args:
            players_df: DataFrame with player stats
            top_n: Number of top players to return
            
        Returns:
            DataFrame with top N players sorted by efficiency (all columns preserved)
        """
        if players_df.empty:
            return players_df
        
        # Debug: Verify team column exists and check type
        has_team = 'team' in players_df.columns
        team_backup = None  # Initialize backup
        print(f"[rank_players] Input has 'team': {has_team}")
        if has_team:
            team_backup = players_df['team'].copy()  # Backup entire team column
            print(f"  Input team type: {players_df['team'].dtype}")
            print(f"  Input team sample: {players_df['team'].head(3).tolist()}")
        
        # Calculate efficiency if not already done
        if "efficiency" not in players_df.columns:
            players_df = self.calculate_player_efficiency(players_df)
        
        # Sort by efficiency and take top N
        ranked_df = players_df.sort_values("efficiency", ascending=False).head(top_n).copy()
        
        # Add rank column (DO NOT assign rank to 'team' column)
        ranked_df["rank"] = range(1, len(ranked_df) + 1)
        
        # Verify team column integrity
        if has_team and team_backup is not None:
            if 'team' not in ranked_df.columns:
                print("  ❌ CRITICAL: team column missing after ranking! Restoring...")
                # Restore from backup using index alignment
                ranked_df['team'] = team_backup.loc[ranked_df.index]
            elif ranked_df['team'].dtype in ['int64', 'float64']:
                print(f"  ❌ CRITICAL: team column is numeric ({ranked_df['team'].dtype})! Restoring...")
                ranked_df['team'] = team_backup.loc[ranked_df.index]
            else:
                print(f"  ✓ team column preserved correctly")
                print(f"  Output team type: {ranked_df['team'].dtype}")
                print(f"  Output team sample: {ranked_df['team'].head(5).tolist()}")
                print(f"  Unique teams: {ranked_df['team'].nunique()}")
        
        return ranked_df
    
    def calculate_team_standings(self, team_stats_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate team standings with point differential
        
        Args:
            team_stats_df: DataFrame with team statistics
            
        Returns:
            DataFrame with team standings
        """
        if team_stats_df.empty:
            return team_stats_df
        
        df = team_stats_df.copy()
        
        # Calculate point differential
        df["point_differential"] = df["points_for"] - df["points_against"]
        
        # Calculate winning percentage
        df["win_pct"] = df["wins"] / (df["wins"] + df["losses"])
        df["win_pct"] = df["win_pct"].fillna(0)
        
        # Calculate points per game
        df["ppg"] = df["points_for"] / df["games_played"]
        df["opp_ppg"] = df["points_against"] / df["games_played"]
        
        # Sort by wins (descending) and point differential (descending)
        df = df.sort_values(["wins", "point_differential"], ascending=[False, False])
        
        # Add overall rank
        df["overall_rank"] = range(1, len(df) + 1)
        
        return df
    
    def get_conference_standings(self, team_stats_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get standings separated by conference
        
        Args:
            team_stats_df: DataFrame with team statistics
            
        Returns:
            Tuple of (Eastern Conference standings, Western Conference standings)
        """
        if team_stats_df.empty:
            return pd.DataFrame(), pd.DataFrame()
        
        # Calculate standings first
        standings_df = self.calculate_team_standings(team_stats_df)
        
        # Split by conference
        east_df = standings_df[standings_df["conference"] == "East"].copy()
        west_df = standings_df[standings_df["conference"] == "West"].copy()
        
        # Add conference rank
        east_df["conf_rank"] = range(1, len(east_df) + 1)
        west_df["conf_rank"] = range(1, len(west_df) + 1)
        
        return east_df, west_df
    
    def get_top_players_by_stat(self, players_df: pd.DataFrame, stat: str, top_n: int = 10) -> pd.DataFrame:
        """
        Get top N players for a specific stat
        
        Args:
            players_df: DataFrame with player stats
            stat: Stat column to rank by (e.g., 'pts', 'reb', 'ast')
            top_n: Number of top players to return
            
        Returns:
            DataFrame with top N players for the stat
        """
        if players_df.empty or stat not in players_df.columns:
            return pd.DataFrame()
        
        # Filter players with minimum games played
        if "games_played" in players_df.columns:
            df = players_df[players_df["games_played"].fillna(0) >= 5].copy()
        else:
            df = players_df.copy()
        
        # Sort by stat
        df = df.sort_values(by=stat, ascending=False).head(top_n)  # type: ignore
        
        # Add rank
        df["rank"] = range(1, len(df) + 1)
        
        return df
    
    def calculate_team_rankings(self, team_stats_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate comprehensive team rankings
        
        Args:
            team_stats_df: DataFrame with team statistics
            
        Returns:
            DataFrame with team rankings
        """
        if team_stats_df.empty:
            return team_stats_df
        
        df = self.calculate_team_standings(team_stats_df)
        
        # Select key columns for display
        columns_to_keep = [
            "overall_rank", "team_name", "conference", 
            "wins", "losses", "win_pct",
            "points_for", "points_against", "point_differential",
            "ppg", "opp_ppg", "games_played"
        ]
        
        columns_to_keep = [col for col in columns_to_keep if col in df.columns]
        
        return df[columns_to_keep]
    
    def get_player_full_name(self, row: pd.Series) -> str:
        """
        Get player's full name from DataFrame row
        
        Args:
            row: DataFrame row with player data
            
        Returns:
            Full name as string
        """
        first_name = row.get("first_name", "")
        last_name = row.get("last_name", "")
        return f"{first_name} {last_name}".strip()
