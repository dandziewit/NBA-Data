"""
Test script to verify NBA Analyzer components work
"""
import sys
from data_fetcher import NBADataFetcher
from stats_calculator import NBAStatsCalculator
from projections import NBAProjections

def test_basic_functionality():
    """Test basic functionality without making API calls"""
    print("="*60)
    print("NBA Analyzer - Component Test")
    print("="*60)
    
    # Test 1: Module imports
    print("\n[1/5] Testing module imports...")
    try:
        fetcher = NBADataFetcher()
        calculator = NBAStatsCalculator()
        projector = NBAProjections()
        print("  SUCCESS: All modules imported and initialized")
    except Exception as e:
        print(f"  ERROR: {e}")
        return False
    
    # Test 2: Configuration
    print("\n[2/5] Checking configuration...")
    print(f"  - Season: {fetcher.current_season}")
    print(f"  - Total season games: {projector.total_season_games}")
    
    # Test 3: Test with sample data
    print("\n[3/5] Testing with sample data...")
    import pandas as pd
    
    # Create sample player data
    sample_players = pd.DataFrame({
        'id': [1, 2, 3],
        'first_name': ['LeBron', 'Stephen', 'Kevin'],
        'last_name': ['James', 'Curry', 'Durant'],
        'pts': [25.5, 28.3, 26.8],
        'reb': [7.2, 5.1, 6.9],
        'ast': [7.8, 6.4, 5.2],
        'stl': [1.2, 1.5, 0.9],
        'blk': [0.8, 0.3, 1.1],
        'games_played': [50, 55, 48],
        'min': [35.2, 34.5, 36.1]
    })
    
    # Test efficiency calculation
    try:
        players_with_eff = calculator.calculate_player_efficiency(sample_players)
        print(f"  SUCCESS: Efficiency calculated for {len(players_with_eff)} players")
        print(f"  - Top player efficiency: {players_with_eff['efficiency'].max():.2f}")
    except Exception as e:
        print(f"  ERROR: Efficiency calculation failed: {e}")
        return False
    
    # Test 4: Rankings
    print("\n[4/5] Testing player rankings...")
    try:
        ranked = calculator.rank_players(players_with_eff, top_n=3)
        print(f"  SUCCESS: Ranked {len(ranked)} players")
        if not ranked.empty:
            top_player = ranked.iloc[0]
            print(f"  - #1: {top_player['first_name']} {top_player['last_name']} (Eff: {top_player['efficiency']:.2f})")
    except Exception as e:
        print(f"  ERROR: Ranking failed: {e}")
        return False
    
    # Test 5: Projections
    print("\n[5/5] Testing projections...")
    try:
        projected = projector.project_player_season_stats(players_with_eff)
        print(f"  SUCCESS: Projections calculated for {len(projected)} players")
        if 'projected_total_games' in projected.columns:
            print(f"  - Projected games range: {projected['projected_total_games'].min()}-{projected['projected_total_games'].max()}")
    except Exception as e:
        print(f"  ERROR: Projections failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("All tests passed! The application is ready to use.")
    print("="*60)
    print("\nTo run the app, use: streamlit run app.py")
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
