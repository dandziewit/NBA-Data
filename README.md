# NBA Data Analyzer 🏀

An interactive web-based NBA 2025-2026 season analyzer built with Streamlit.

## 🚀 Live App

**[Open the app in your browser](https://nba-data-az48in6pu8ndseqnnyrnj7.streamlit.app/)** - No installation needed!

## Features

- 📊 Player rankings and statistics
- 📈 Performance visualizations
- 🎯 Three-point shooting analytics
- 📉 Statistical comparisons
- 🏆 MVP scoring calculations

## Quick Start

### Option 1: PowerShell (Recommended for PowerShell users)
```powershell
.\start.ps1
```

### Option 2: Command Prompt (CMD)
```cmd
start.bat
```

### Option 3: Manual Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Windows (CMD):
.\.venv\Scripts\activate.bat
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Deploy to Streamlit Cloud

You can host this app for free and get a shareable URL in minutes.

1. Push this project to GitHub (already pushed to `dandziewit/NBA-Data`).
2. Go to https://streamlit.io/cloud and sign in with GitHub.
3. Click "New app" and select the repo `dandziewit/NBA-Data`.
4. Set "Main file path" to `app.py`.
5. Click "Deploy" — you'll get a live URL like `https://<your-app>.streamlit.app`.

Optional:
- Add secrets in `.streamlit/secrets.toml` if needed (e.g., API keys).
- Customize theme and server settings in `.streamlit/config.toml`.

### Update the Live App

The deployed app auto-updates on each push to `main`.

```powershell
Push-Location "C:\\Users\\Damiel Dziewit\\.vscode\\projects\\NBA Data Anylyzer"
git add -A
git commit -m "Update app"
git push
Pop-Location
```

## What happens after running?

The application will automatically:
1. Create a Python virtual environment (if needed)
2. Install all required dependencies
3. Start the Streamlit server
4. Open the web app in your default browser at `http://localhost:8501`

## Controls

- **Top menu**: Select different analysis sections
- **Left sidebar**: Adjust filters and parameters
- **Tabs**: Switch between different views (Rankings, Visualizations, Standings, etc.)
- **Hover**: Hover over charts to see detailed player and team information

## Stop the Server

Press `Ctrl+C` in the terminal to stop the server.

## Requirements

- Python 3.8+
- See `requirements.txt` for package dependencies

## Troubleshooting

**Port already in use:**
```
streamlit run app.py --server.port=8502
```

**Virtual environment not activating:**
- Try using Command Prompt (CMD) instead of PowerShell
- Ensure you're running the command from the project directory

**Module not found errors:**
- Ensure you've activated the virtual environment
- Run `pip install -r requirements.txt` again

## Project Structure

```
├── app.py                 # Main Streamlit application
├── data_fetcher.py        # NBA API data retrieval
├── stats_calculator.py    # Statistical calculations
├── projections.py         # Season projections and predictions
├── config.py              # Configuration settings
├── start.ps1              # PowerShell startup script
├── start.bat              # Command Prompt startup script
├── requirements.txt       # Python dependencies
├── .streamlit/            # Streamlit Cloud config & secrets
│   ├── config.toml        # Theme/server settings
│   └── secrets.toml       # Optional secrets for deployment
└── README.md              # This file
```
