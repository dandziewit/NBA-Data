# NBA Data Analyzer

An interactive analytics dashboard built with **Python** and **Streamlit** to explore NBA player performance through **rankings, efficiency metrics, projections, and visualizations**.

It retrieves live league data, calculates derived statistics (e.g., scoring efficiency and three-point performance), and presents results in an interactive browser UI.

## Live Demo

Launch the app on Streamlit Community Cloud:  
https://nba-data-az48in6pu8ndseqnnyrnj7.streamlit.app/

---

## Dashboard Preview

### Player Statistics
![Player Stats](stats.png)

### Performance Charts
![Performance Charts](charts.png)

---

## Features

- Player rankings based on efficiency and core box-score metrics
- Interactive visualizations for scoring distribution, efficiency trends, and three-point shooting
- Season projection tools for estimating player outcomes and milestone pacing
- Configurable filters (minimum games played, number of results displayed)
- Cached data retrieval to reduce API calls and improve UI responsiveness
- Modular analytics pipeline separating ingestion, processing, projections, and presentation

---

## Tech Stack

- **Language:** Python  
- **Data Processing:** Pandas, NumPy  
- **Visualization / UI:** Streamlit  
- **Data Source:** NBA statistics API  
- **Testing:** Python-based component testing  

---

## Project Structure / Architecture

The app follows a modular analytics pipeline that separates data ingestion, computation, projections, and presentation:

```text
NBA API
  ͏
data_fetcher.py
  ͏
stats_calculator.py
  ͏
projections.py
  ͏
app.py (Streamlit dashboard)
```

### Module Responsibilities

- **data_fetcher.py**  
  Retrieves player statistics from the NBA data source and normalizes the dataset for downstream processing.

- **stats_calculator.py**  
  Computes derived metrics including efficiency rankings, scoring statistics, and player comparisons.

- **projections.py**  
  Implements projection utilities used to estimate season outcomes and milestone pacing.

- **app.py**  
  Streamlit presentation layer responsible for rendering tables, visualizations, dashboards, and user controls.

- **config.py**  
  Centralized runtime constants such as cache duration, display limits, and threshold settings.

---

## Setup

### Prerequisites
- Python 3.8+
- Windows PowerShell or Command Prompt

### Option A  PowerShell
```powershell
.
start.ps1
```

### Option B  Command Prompt
```bat
start.bat
```

### Option C  Manual Setup
```powershell
python -m venv .venv
.
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

---

## Usage

After startup, open:

- http://localhost:8501

(if the browser does not launch automatically)

Use the sidebar controls to:
- Set the number of players displayed
- Configure minimum games played
- Refresh cached data

Navigate between tabs to explore:
- Player rankings
- Visual analytics and charts

---

## Configuration

Runtime settings are defined in `config.py`, including:
- Cache TTL
- Default display limits
- Minimum games threshold
- Season length assumptions
- Milestone thresholds used in projections

Updating these values lets you tune behavior without modifying the core analytics modules.

---

## Testing

Run the lightweight component smoke test:

```bash
python test_app.py
```

This validates:
- Module initialization
- Core calculation paths
- Ranking and projection execution with sample data

---

## Deployment

This app can be deployed using **Streamlit Community Cloud**.

### Deployment Steps
1. Push the repository to GitHub
2. Create a new Streamlit app linked to the repository
3. Set the entry point to `app.py`
4. Configure environment variables/secrets if required
5. Deploy and verify data retrieval and chart rendering

---

## Why I Built This

I built this project to explore how sports data can be transformed into meaningful insights using Python analytics tools. The goal was to design a lightweight but structured pipeline that retrieves live data, computes derived statistics, and presents results through an interactive dashboard.

This project helped me practice building modular data pipelines, working with real-world datasets, and developing interactive analytical applications.

---

## Contributing

- Create a feature branch from `main`
- Keep changes focused and testable
- Add or update tests when modifying logic
- Run `python test_app.py` before opening a PR

When submitting a PR, include:
- A clear summary of changes
- Rationale and impact
- Screenshots for UI updates

---

## License

MIT License

---

## Author

**Daniel Dziewit**  
GitHub: https://github.com/dandziewit
