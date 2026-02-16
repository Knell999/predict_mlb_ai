"""
데이터 로딩/조회 도구
utils.py의 데이터 함수들을 Agent Tool로 래핑합니다.
"""

import sys
import os
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


def _fuzzy_search(name: str, all_names, limit: int = 5) -> List[str]:
    """간단한 부분 문자열 매칭 검색"""
    matches = [n for n in all_names if name.lower() in n.lower()]
    return sorted(matches)[:limit]


@tool
def get_player_stats(player_name: str, player_type: str = "batter") -> Dict[str, Any]:
    """특정 선수의 전체 커리어 통계를 조회합니다.

    Args:
        player_name: 선수 이름 (예: "Mike Trout")
        player_type: "batter" 또는 "pitcher"

    Returns:
        선수 통계 딕셔너리 또는 오류 메시지
    """
    from utils import load_data, load_pitcher_data

    df = load_data() if player_type == "batter" else load_pitcher_data()
    player_data = df[df['PlayerName'] == player_name]

    if player_data.empty:
        suggestions = _fuzzy_search(player_name, df['PlayerName'].unique())
        return {"error": f"선수 '{player_name}'을(를) 찾을 수 없습니다", "suggestions": suggestions}

    return {
        "player_name": player_name,
        "player_type": player_type,
        "seasons": len(player_data),
        "season_range": [int(player_data['Season'].min()), int(player_data['Season'].max())],
        "data": player_data.to_dict(orient="records"),
    }


@tool
def get_league_averages(player_type: str, metrics: List[str]) -> Dict[str, Any]:
    """시즌별 리그 평균을 계산합니다.

    Args:
        player_type: "batter" 또는 "pitcher"
        metrics: 지표 컬럼명 목록 (예: ["BattingAverage", "HomeRuns"])

    Returns:
        시즌별 리그 평균 딕셔너리
    """
    from utils import load_data, load_pitcher_data, calculate_league_averages

    df = load_data() if player_type == "batter" else load_pitcher_data()
    valid_metrics = [m for m in metrics if m in df.columns]
    if not valid_metrics:
        return {"error": "유효한 지표가 없습니다", "available": list(df.columns)}

    avg_df = calculate_league_averages(df, valid_metrics)
    return {
        "metrics": valid_metrics,
        "data": avg_df.to_dict(orient="records"),
    }


@tool
def search_players(query: str, player_type: str = "batter") -> List[str]:
    """선수 이름을 부분 문자열로 검색합니다.

    Args:
        query: 검색 문자열
        player_type: "batter" 또는 "pitcher"

    Returns:
        매칭되는 선수 이름 목록 (최대 20명)
    """
    from utils import load_data, load_pitcher_data

    df = load_data() if player_type == "batter" else load_pitcher_data()
    all_names = df['PlayerName'].unique()
    matches = [n for n in all_names if query.lower() in n.lower()]
    return sorted(matches)[:20]


@tool
def get_player_season_stats(
    player_name: str, season: int, player_type: str = "batter"
) -> Dict[str, Any]:
    """특정 선수의 특정 시즌 기록을 조회합니다.

    Args:
        player_name: 선수 이름
        season: 시즌 연도 (예: 2023)
        player_type: "batter" 또는 "pitcher"

    Returns:
        해당 시즌 통계 딕셔너리
    """
    from utils import load_data, load_pitcher_data

    df = load_data() if player_type == "batter" else load_pitcher_data()
    data = df[(df['PlayerName'] == player_name) & (df['Season'] == season)]

    if data.empty:
        return {"error": f"{player_name}의 {season} 시즌 데이터가 없습니다"}

    return data.to_dict(orient="records")[0]
