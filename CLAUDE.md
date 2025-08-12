# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive MLB (Major League Baseball) player statistics and prediction web application built with Streamlit. It provides player record lookup, trend analysis, and performance prediction using machine learning (Prophet algorithm).

## Key Commands

### Running the Application
```bash
# Main application entry point
streamlit run app.py

# Alternative entry point (if needed)
python main.py
```

### AI Analysis Setup (Optional)
```bash
# Install AI analysis dependencies
pip install langchain langchain-google-genai google-generativeai

# Set up environment variable for Google AI API
export GOOGLE_AI_API_KEY="your_api_key_here"

# Check AI feature status
python -c "from player_analysis_ai import get_ai_analysis_status; print(get_ai_analysis_status())"
```

### Data Management
```bash
# Test data update functionality
python test_data_update.py

# Update MLB data manually
python update_data.py

# PyBaseball data collection
python pybaseball_processor.py

# MLB API data collection  
python data_processor.py

# Auto-scheduled data updates
python auto_update.py --mode scheduler

# One-time data update
python auto_update.py --mode once

# Check data quality
python data_quality_checker.py
```

### Data Update Options
```bash
# PyBaseball method (recommended)
python update_data.py --method pybaseball --start-year 2024

# MLB API method
python update_data.py --method mlb-api --start-year 2024

# With backup
python update_data.py --method pybaseball --backup

# Specific year range
python update_data.py --method mlb-api --start-year 2023 --end-year 2024
```

## Project Architecture

### Core Application Structure
- **app.py**: Main Streamlit application entry point with sidebar navigation
- **main.py**: Alternative entry point (currently unused)
- **home.py**: Home page with application overview
- **search.py**: Player statistics lookup functionality with AI analysis integration
- **predict.py**: Performance prediction using Prophet
- **trend.py**: League trend analysis and visualization
- **compare.py**: Player comparison features
- **utils.py**: Shared utility functions and chart styling
- **player_analysis_ai.py**: AI-powered player analysis using LangChain and Google Gemini

### Data Layer
- **data_processor.py**: MLB official API data collection
- **pybaseball_processor.py**: PyBaseball library data collection
- **update_data.py**: Unified data update orchestrator
- **auto_update.py**: Scheduled data updates with season-aware scheduling
- **data_quality_checker.py**: Data validation and quality checks
- **data_status.py**: Data status monitoring for the UI

### Configuration & Internationalization
- **config.py**: Application configuration and file paths
- **i18n.py**: Multi-language support (Korean, English, Japanese)
- **app_metrics.py**: Application performance monitoring

### Data Files
- **data/mlb_batter_stats_2000_2023.csv**: Historical batter statistics
- **data/mlb_pitcher_stats_2000_2023.csv**: Historical pitcher statistics

## Development Workflow

### Data Update Schedule
- **Season (March-October)**: Daily at 6 AM
- **Off-season (November-February)**: Weekly on Sundays at 8 AM

### Package Management
- Uses both `pyproject.toml` (primary) and `requirements.txt` (generated)
- Python 3.13+ required
- Key dependencies: Streamlit, Prophet, Pandas, Matplotlib, Seaborn

### Data Sources
1. **PyBaseball** (preferred): More stable and faster
2. **MLB Official API**: More current data but with rate limits

### Testing
- **test_data_update.py**: Comprehensive test suite for data update functionality
- Tests PyBaseball integration, MLB API connectivity, and existing data validation

## Important Notes

- The application requires Korean font support (H2GTRM.TTF in font/ directory)
- Logs are stored in logs/ directory with date-based naming
- Data backup is recommended before major updates
- Network connectivity required for data collection
- API rate limits may affect MLB official API data collection speed

## File Structure Context

The project follows a modular architecture where each major feature (search, predict, trend, compare) has its own module. The data layer is abstracted through processor classes that handle different data sources. The application supports multiple languages and includes comprehensive logging and monitoring capabilities.