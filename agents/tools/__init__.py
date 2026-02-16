"""
Agent 도구 레지스트리
각 Agent에 바인딩할 도구 그룹을 정의합니다.
"""

from agents.tools.data_tools import (
    get_player_stats,
    get_league_averages,
    search_players,
    get_player_season_stats,
)
from agents.tools.stats_tools import (
    calculate_career_averages,
    compare_to_league,
    detect_trend,
)
from agents.tools.prediction_tools import (
    run_prophet_forecast,
    assess_prediction_data_adequacy,
)
from agents.tools.quality_tools import (
    check_file_existence,
    check_data_structure,
    check_data_quality,
    get_season_statistics,
    detect_statistical_anomalies,
)
from agents.tools.similarity_tools import (
    find_similar_players,
    find_players_by_criteria,
)
from agents.tools.update_tools import (
    run_pybaseball_update,
    run_mlb_api_update,
    create_data_backup,
    get_current_data_stats,
)

CONVERSATIONAL_TOOLS = [
    get_player_stats, get_league_averages, search_players,
    get_player_season_stats, calculate_career_averages,
    compare_to_league, detect_trend, run_prophet_forecast,
    find_similar_players,
]

PREDICTION_TOOLS = [
    get_player_stats, run_prophet_forecast,
    assess_prediction_data_adequacy, get_league_averages,
    find_similar_players, detect_trend,
]

QUALITY_TOOLS = [
    check_file_existence, check_data_structure, check_data_quality,
    get_season_statistics, detect_statistical_anomalies,
]

SIMILARITY_TOOLS = [
    find_similar_players, find_players_by_criteria,
    get_player_stats, get_league_averages, calculate_career_averages,
]

REPORT_TOOLS = [
    get_player_stats, get_league_averages, calculate_career_averages,
    compare_to_league, detect_trend, run_prophet_forecast,
    find_similar_players,
]

UPDATE_TOOLS = [
    run_pybaseball_update, run_mlb_api_update,
    create_data_backup, get_current_data_stats,
    check_data_quality, check_data_structure,
]
