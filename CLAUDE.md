# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive MLB (Major League Baseball) player statistics and prediction web application built with Streamlit. It provides player record lookup, trend analysis, and performance prediction using machine learning (Prophet algorithm), with optional AI-powered analysis using Google Gemini.

## Key Commands

### Running the Application
```bash
# Main application entry point (recommended)
streamlit run app.py

# With UV package manager (if installed)
uv run streamlit run app.py
```

### Package Management
```bash
# Install dependencies with UV (recommended)
uv sync

# Install dependencies with pip
pip install -r requirements.txt

# Add new dependency
uv add <package-name>

# Generate requirements.txt from pyproject.toml
uv pip compile pyproject.toml -o requirements.txt
```

### AI Analysis Setup (Optional)
```bash
# AI dependencies already in pyproject.toml
# Set up .env file with API key
echo "GOOGLE_AI_API_KEY=your_key_here" > .env

# Check AI feature status
python -c "from player_analysis_ai import get_ai_analysis_status; print(get_ai_analysis_status())"
```

### Data Management
```bash
# Update MLB data (auto-selects best method)
python update_data.py --start-year 2024

# PyBaseball method (recommended - faster and more stable)
python update_data.py --method pybaseball --start-year 2024 --backup

# MLB API method (slower but more current)
python update_data.py --method mlb-api --start-year 2024

# Schedule automatic updates (season-aware)
python auto_update.py --mode scheduler

# One-time update
python auto_update.py --mode once

# Check data quality
python data_quality_checker.py

# Test data update functionality
python test_data_update.py
```

## Project Architecture

### Application Flow
1. **app.py** loads environment variables (.env) first, then initializes Streamlit config
2. Session state manages language preference (`st.session_state.lang`)
3. Page modules are loaded dynamically based on sidebar selection
4. Data is cached using `@st.cache_data` with 1-hour TTL
5. All text content goes through **i18n.py** for multi-language support

### Core Application Structure
- **app.py**: Main entry point - handles sidebar navigation, language switching, and page routing
- **home.py**: Home page with app overview
- **search.py**: Player statistics lookup with AI analysis integration (타자/투수, 선수기준/시즌기준)
- **predict.py**: Performance prediction using Prophet algorithm
- **trend.py**: League-wide trend analysis and visualization
- **compare.py**: Side-by-side player comparison
- **utils.py**: Shared utilities - data loading, chart styling, font management
- **player_analysis_ai.py**: AI analysis using LangChain + Google Gemini (gemini-2.5-pro)

### Data Layer Architecture
The data layer uses a **dual-source strategy**:

1. **pybaseball_processor.py**: PyBaseball library (preferred)
   - Faster and more stable
   - Uses `batting_stats()` and `pitching_stats()`

2. **data_processor.py**: MLB Stats API
   - More current data
   - Rate-limited, slower
   - Uses REST API: `https://statsapi.mlb.com/api/v1`

3. **update_data.py**: Orchestrator
   - Auto-selects best method
   - Falls back to MLB API if PyBaseball fails
   - Handles data merging and deduplication

4. **auto_update.py**: Scheduler
   - Season-aware scheduling (daily in-season, weekly off-season)
   - Uses `schedule` library

### Configuration & Internationalization
- **config.py**: Centralized paths (BASE_DIR, DATA_DIR, FONT_PATH, etc.)
- **i18n.py**: Three-language support (ko/en/ja) using dictionary lookups
  - `get_text(key, lang)` - retrieves localized text
  - Language stored in `st.session_state.lang`
- **app_metrics.py**: Performance tracking (page views, response times)

### AI Analysis Architecture
- **player_analysis_ai.py** uses LangChain with Google Gemini
- Two prompt templates: `batter_analysis_prompt` and `pitcher_analysis_prompt`
- Converts DataFrame to text summaries before sending to LLM
- Optional feature - gracefully degrades if API key not configured
- Analysis includes: career highlights, key metrics, league comparison, trends, insights

### Data Schema
**Batter Stats CSV:**
- Season, PlayerID, PlayerName, Team, GamesPlayed, AtBats, Runs, Hits, HomeRuns, RBIs, StolenBases, Walks, StrikeOuts, BattingAverage, OnBasePercentage, SluggingPercentage, OPS

**Pitcher Stats CSV:**
- Season, PlayerID, PlayerName, Team, Wins, Losses, EarnedRunAverage, Whip, StrikeOuts, InningsPitched, Walks, HitsAllowed

### Key Design Patterns

1. **Caching Strategy**: All data loading uses `@st.cache_data(ttl=3600)` for 1-hour cache
2. **Graceful Degradation**: Missing fonts, images, or AI features don't break the app
3. **Modular Pages**: Each feature has its own `run_<feature>(lang)` function
4. **Shared League Averages**: Calculated once in search.py, reused for comparisons
5. **Player Images**: Dynamically loaded from MLB CDN using PlayerID
6. **Error Handling**: Try/except blocks with user-friendly warnings, fallback to sample data

## Development Workflow

### Data Update Schedule
- **Season (March-October)**: Daily at 6 AM
- **Off-season (November-February)**: Weekly on Sundays at 8 AM

### Package Management Notes
- Primary: `pyproject.toml` (UV/Hatch format)
- Generated: `requirements.txt` (for compatibility)
- Python 3.11+ required (system: 3.9.6, venv: 3.11.13)
- Package manager: UV (recommended) or pip
- Key dependencies: streamlit, prophet, pandas, matplotlib, seaborn, langchain, google-generativeai

### Adding New Features
1. Create new module file (e.g., `new_feature.py`)
2. Define `run_new_feature(lang="ko")` function
3. Add i18n entries in `i18n.py` for all three languages
4. Update sidebar menu in `app.py` with new option
5. Add routing logic in `main()` function
6. Update CLAUDE.md with new feature documentation

### Testing Data Updates
```bash
# Test with small year range first
python update_data.py --method pybaseball --start-year 2023 --end-year 2023

# Verify data integrity
python data_quality_checker.py

# Check logs
tail -100 logs/app_$(date +%Y%m%d).log
```

## Important Notes

### Font Requirements
- Korean font required: `font/H2GTRM.TTF`
- Loaded in `utils.py` via `set_chart_style()`
- Matplotlib configured to use this font for Korean text rendering
- Falls back to system fonts (Malgun Gothic, AppleGothic) if missing

### Environment Variables
- `.env` file loaded at app startup (via python-dotenv)
- `GOOGLE_AI_API_KEY`: Required for AI analysis features
- Other optional vars: LOG_LEVEL, custom data paths

### Logging
- Logs stored in `logs/` directory
- Format: `app_YYYYMMDD.log`
- Configured in `app_metrics.py`

### Streamlit-Specific Considerations
- `st.set_page_config()` MUST be the first Streamlit command (see app.py:11)
- Session state used for language preference persistence
- `st.rerun()` called when language changes to refresh UI
- All page modules receive `lang` parameter for localization

### Data Collection Limitations
- MLB API has rate limits - large year ranges may be slow
- PyBaseball cache can become stale - clear if issues arise
- Network connectivity required for data updates
- Player images may fail to load from CDN - gracefully handled

### Current Data Range
- Batters: 2000-2025 (4,502 records)
- Pitchers: 2000-2025 (2,813 records)
- Updated: February 2026