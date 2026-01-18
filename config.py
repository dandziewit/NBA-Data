"""
Configuration settings for NBA Analyzer
"""

# API Configuration
API_BASE_URL = "https://api.balldontlie.io/v1"
API_TIMEOUT = 10  # seconds
API_RATE_LIMIT_DELAY = 0.6  # seconds between requests

# Season Configuration
CURRENT_SEASON = 2025  # Will auto-detect latest available (tries 2025, 2024, 2023)
TOTAL_SEASON_GAMES = 82

# Data Fetching Limits
MAX_PLAYERS_TO_FETCH = 500  # Limit player API calls
MAX_GAMES_PAGES = 10  # Limit game data fetching

# Player Filters
MIN_GAMES_PLAYED_DEFAULT = 5
MIN_MINUTES_PLAYED_DEFAULT = 10.0

# Team Configuration
PLAYOFF_SPOTS_PER_CONFERENCE = 8

# Display Configuration
DEFAULT_TOP_PLAYERS = 50
MAX_TOP_PLAYERS = 100
DEFAULT_TOP_TEAMS = 30

# Cache Configuration
CACHE_TTL_SECONDS = 3600  # 1 hour

# Stat Columns
PLAYER_STAT_COLUMNS = ["pts", "reb", "ast", "stl", "blk", "fg_pct", "fg3_pct", "ft_pct", "turnover"]
TEAM_STAT_COLUMNS = ["wins", "losses", "points_for", "points_against", "point_differential"]

# Milestone Thresholds
MILESTONE_POINTS = [1500, 2000, 2500]
MILESTONE_REBOUNDS = [500, 750, 1000]
MILESTONE_ASSISTS = [500, 750, 1000]
MILESTONE_STEALS = [100, 150, 200]
MILESTONE_BLOCKS = [100, 150, 200]
