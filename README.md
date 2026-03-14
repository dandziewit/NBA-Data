# NBA Data Analyzer

## Overview
NBA Data Analyzer is a Streamlit application for exploring NBA player performance with rankings, projections, and interactive visualizations. The app fetches live league data, applies derived metrics, and presents analysis through a browser-based dashboard.

## Features
- Player rankings by efficiency and core box-score metrics
- Interactive visualizations for scoring, efficiency, and three-point performance
- Season projection utilities for player outcomes and milestone pace
- Configurable filters for minimum games played and result size
- Cached data loading to reduce API load and improve UI responsiveness

## Architecture
The codebase is organized into a lightweight analytics pipeline:
- `data_fetcher.py`: Retrieves and normalizes upstream NBA data
- `stats_calculator.py`: Computes rankings and derived statistics
- `projections.py`: Generates season and milestone projections
- `app.py`: Streamlit presentation layer and user interactions
- `config.py`: Centralized runtime constants

Execution flow:
1. Fetch and cache player data
2. Calculate efficiency and ranking metrics
3. Apply projection and scoring utilities
4. Render tables, KPIs, and charts in Streamlit

## Setup
### Prerequisites
- Python 3.8+
- Windows PowerShell or Command Prompt

### Option A: PowerShell
```powershell
.\start.ps1
```

### Option B: Command Prompt
```cmd
start.bat
```

### Option C: Manual
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

## Usage
After startup, open `http://localhost:8501` if the browser does not open automatically.

Use the sidebar to:
- Set number of players displayed
- Set minimum games played
- Refresh cached data

Use tabs to switch between:
- Rankings table
- Visual analytics

## Configuration
Runtime settings are defined in `config.py`, including:
- Cache TTL
- Default display limits
- Minimum games threshold
- Season length and playoff spot assumptions
- Milestone thresholds for projections

Adjust values in `config.py` to tune behavior across modules.

## Testing
Run the lightweight component smoke test:
```powershell
python test_app.py
```

What it validates:
- Module initialization
- Core calculation paths
- Ranking and projection execution with sample data

## Deployment
The app can be deployed on Streamlit Community Cloud.

High-level process:
1. Push the repository to GitHub
2. Create a new Streamlit app and point it to `app.py`
3. Configure environment/secrets if required
4. Deploy and verify charts/data rendering

## Contribution Guidelines
- Create a feature branch from `main`
- Keep changes scoped and testable
- Update or add tests for behavioral changes
- Run `python test_app.py` before opening a PR
- Submit a pull request with:
	- Clear summary of changes
	- Rationale and impact
	- Screenshots for UI updates
