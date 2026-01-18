"""
NBA Projections Module
Calculates season projections for players and teams based on current averages
"""

import pandas as pd
import numpy as np
from typing import Dict

class NBAProjections:
    """
    Class for calculating NBA season projections
    """
    
    def __init__(self, total_season_games: int = 82):
        """
        Initialize projections calculator
        
        Args:
            total_season_games: Total games in a regular NBA season (default 82)
        """
        self.total_season_games = total_season_games
    
    def project_player_season_stats(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """
        Project full season statistics for players based on current averages
        
        Args:
            players_df: DataFrame with player season averages
            
        Returns:
            DataFrame with projected season totals added
        """
        if players_df.empty:
            return players_df
        
        df = players_df.copy()
        
        # Ensure games_played column exists
        if "games_played" not in df.columns:
            df["games_played"] = 0
        
        # Get games played so far
        games_played = df["games_played"].fillna(0)
        
        # Estimate remaining games (assuming player plays similar percentage of remaining games)
        # Calculate projected total games player will play
        season_progress = games_played / self.total_season_games
        season_progress = season_progress.clip(lower=0.01, upper=1.0)  # Avoid division by zero
        
        projected_total_games = (games_played / season_progress).clip(upper=self.total_season_games)
        df["projected_total_games"] = projected_total_games.astype(int)
        
        # Calculate remaining games
        df["remaining_games"] = (projected_total_games - games_played).clip(lower=0)
        
        # Project season totals for key stats (per-game averages * projected total games)
        stat_columns = ["pts", "reb", "ast", "stl", "blk", "fg_pct", "fg3_pct", "ft_pct"]
        
        for stat in stat_columns:
            if stat in df.columns:
                if stat.endswith("_pct"):
                    # Percentages don't get projected, just carried forward
                    df[f"projected_{stat}"] = df[stat]
                else:
                    # Total stats get projected
                    df[f"projected_season_{stat}"] = (df[stat] * df["projected_total_games"]).round(1)
        
        # Project efficiency for full season
        if "efficiency" in df.columns:
            df["projected_season_efficiency"] = df["efficiency"] * df["projected_total_games"]
        
        return df
    
    def project_team_season_record(self, team_stats_df: pd.DataFrame) -> pd.DataFrame:
        """
        Project end-of-season team records based on current performance
        
        Args:
            team_stats_df: DataFrame with team statistics
            
        Returns:
            DataFrame with projected season records
        """
        if team_stats_df.empty:
            return team_stats_df
        
        df = team_stats_df.copy()
        
        # Calculate current winning percentage
        total_games = df["wins"] + df["losses"]
        df["current_win_pct"] = (df["wins"] / total_games).fillna(0)
        
        # Calculate remaining games
        df["remaining_games"] = (self.total_season_games - total_games).clip(lower=0)
        
        # Project wins and losses for remaining games
        df["projected_remaining_wins"] = (df["remaining_games"] * df["current_win_pct"]).round(1)
        df["projected_remaining_losses"] = (df["remaining_games"] * (1 - df["current_win_pct"])).round(1)
        
        # Calculate projected final record
        df["projected_total_wins"] = (df["wins"] + df["projected_remaining_wins"]).astype(int)
        df["projected_total_losses"] = (df["losses"] + df["projected_remaining_losses"]).astype(int)
        
        # Project final point differential
        if "point_differential" in df.columns:
            ppg_diff = df["point_differential"] / total_games
            df["projected_point_differential"] = (ppg_diff * self.total_season_games).round(1)
        
        # Project total points
        if "ppg" in df.columns:
            df["projected_total_points_for"] = (df["ppg"] * self.total_season_games).round(1)
        
        if "opp_ppg" in df.columns:
            df["projected_total_points_against"] = (df["opp_ppg"] * self.total_season_games).round(1)
        
        return df
    
    def get_playoff_probability(self, team_stats_df: pd.DataFrame, top_n_per_conference: int = 8) -> pd.DataFrame:
        """
        Estimate playoff probability based on projected wins
        Simple estimation: teams ranked in top N per conference have higher probability
        
        Args:
            team_stats_df: DataFrame with projected team statistics
            top_n_per_conference: Number of playoff spots per conference (default 8)
            
        Returns:
            DataFrame with playoff probability estimates
        """
        if team_stats_df.empty:
            return team_stats_df
        
        # Project season records if not already done
        if "projected_total_wins" not in team_stats_df.columns:
            team_stats_df = self.project_team_season_record(team_stats_df)
        
        df = team_stats_df.copy()
        
        # Rank teams within conference by projected wins
        df = df.sort_values(["conference", "projected_total_wins"], ascending=[True, False])
        
        # Add conference rank
        df["conf_rank"] = df.groupby("conference").cumcount() + 1
        
        # Simple playoff probability estimation
        # Top N teams: high probability, next few: medium, rest: low
        def estimate_playoff_prob(rank):
            if rank <= top_n_per_conference:
                return min(95 + (top_n_per_conference - rank) * 0.5, 99)
            elif rank <= top_n_per_conference + 2:
                return 50 - (rank - top_n_per_conference) * 20
            else:
                return max(5, 30 - (rank - top_n_per_conference) * 5)
        
        df["playoff_probability"] = df["conf_rank"].apply(estimate_playoff_prob)
        
        return df
    
    def get_player_milestone_projections(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate if players are on track for statistical milestones
        (e.g., 2000 points, 500 assists, etc.)
        
        Args:
            players_df: DataFrame with player projections
            
        Returns:
            DataFrame with milestone information
        """
        if players_df.empty:
            return players_df
        
        # Project season stats if not already done
        if "projected_season_pts" not in players_df.columns:
            players_df = self.project_player_season_stats(players_df)
        
        df = players_df.copy()
        
        # Define milestones
        milestones = {
            "2000_pts_pace": df.get("projected_season_pts", 0) >= 2000,
            "1500_pts_pace": df.get("projected_season_pts", 0) >= 1500,
            "500_rebs_pace": df.get("projected_season_reb", 0) >= 500,
            "500_asts_pace": df.get("projected_season_ast", 0) >= 500,
            "100_stls_pace": df.get("projected_season_stl", 0) >= 100,
            "100_blks_pace": df.get("projected_season_blk", 0) >= 100,
        }
        
        for milestone_name, milestone_condition in milestones.items():
            df[milestone_name] = milestone_condition
        
        return df
    
    def calculate_mvp_score(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate a simple MVP score based on efficiency and team success
        This is a simplified metric for demonstration
        
        Args:
            players_df: DataFrame with player stats
            
        Returns:
            DataFrame with MVP score added
        """
        if players_df.empty:
            return players_df
        
        df = players_df.copy()
        
        # Simple MVP score: efficiency + bonus for being on winning team
        # (In reality, MVP considers many more factors)
        if "efficiency" in df.columns:
            df["mvp_score"] = df["efficiency"]
            
            # Normalize to 0-100 scale
            max_eff = df["efficiency"].max()
            if max_eff > 0:
                df["mvp_score"] = (df["efficiency"] / max_eff * 100).round(1)
        
        return df
