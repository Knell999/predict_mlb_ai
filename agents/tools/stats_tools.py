"""
통계 계산 도구
커리어 평균, 리그 비교, 트렌드 분석 등의 통계 연산을 제공합니다.
"""

import sys
import os
from typing import List, Dict, Any
from langchain_core.tools import tool
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@tool
def calculate_career_averages(
    player_name: str, player_type: str, metrics: List[str]
) -> Dict[str, Any]:
    """선수의 커리어 평균을 계산합니다.

    Args:
        player_name: 선수 이름
        player_type: "batter" 또는 "pitcher"
        metrics: 계산할 지표 목록

    Returns:
        지표별 커리어 평균값 딕셔너리
    """
    from utils import load_data, load_pitcher_data

    df = load_data() if player_type == "batter" else load_pitcher_data()
    player_data = df[df['PlayerName'] == player_name]

    if player_data.empty:
        return {"error": f"선수를 찾을 수 없습니다: {player_name}"}

    result = {"player_name": player_name, "seasons": len(player_data)}
    for m in metrics:
        if m in player_data.columns:
            result[m] = round(float(player_data[m].mean()), 4)
    return result


@tool
def compare_to_league(
    player_name: str, player_type: str, season: int, metrics: List[str]
) -> Dict[str, Any]:
    """특정 시즌에서 선수의 성적을 리그 평균과 비교합니다.

    Args:
        player_name: 선수 이름
        player_type: "batter" 또는 "pitcher"
        season: 비교할 시즌 연도
        metrics: 비교할 지표 목록

    Returns:
        선수값, 리그 평균, 차이를 포함하는 딕셔너리
    """
    from utils import load_data, load_pitcher_data, calculate_league_averages

    df = load_data() if player_type == "batter" else load_pitcher_data()
    player_data = df[(df['PlayerName'] == player_name) & (df['Season'] == season)]

    if player_data.empty:
        return {"error": f"{player_name}의 {season} 시즌 데이터가 없습니다"}

    valid_metrics = [m for m in metrics if m in df.columns]
    league_avg = calculate_league_averages(df, valid_metrics)
    league_season = league_avg[league_avg['Season'] == season]

    result = {}
    for m in valid_metrics:
        p_val = float(player_data[m].iloc[0])
        l_val = float(league_season[m].iloc[0]) if not league_season.empty else None
        result[m] = {
            "player": round(p_val, 4),
            "league_avg": round(l_val, 4) if l_val is not None else None,
            "diff": round(p_val - l_val, 4) if l_val is not None else None,
            "above_average": p_val > l_val if l_val is not None else None,
        }
    return result


@tool
def detect_trend(player_name: str, player_type: str, metric: str) -> Dict[str, Any]:
    """선수의 특정 지표 트렌드를 분석합니다.

    Args:
        player_name: 선수 이름
        player_type: "batter" 또는 "pitcher"
        metric: 분석할 지표 컬럼명

    Returns:
        방향, 기울기, 피크/최저 시즌 등의 트렌드 분석 결과
    """
    from utils import load_data, load_pitcher_data

    df = load_data() if player_type == "batter" else load_pitcher_data()
    player_data = df[df['PlayerName'] == player_name].sort_values('Season')

    if player_data.empty or metric not in player_data.columns:
        return {"error": "선수 또는 지표를 찾을 수 없습니다"}

    values = player_data[metric].values.astype(float)
    seasons = player_data['Season'].values.astype(int)

    if len(values) < 2:
        return {
            "player_name": player_name,
            "metric": metric,
            "seasons": 1,
            "direction": "insufficient_data",
            "latest_value": round(float(values[0]), 4),
        }

    coeffs = np.polyfit(range(len(values)), values, 1)

    return {
        "player_name": player_name,
        "metric": metric,
        "seasons": len(values),
        "slope": round(float(coeffs[0]), 6),
        "direction": "improving" if coeffs[0] > 0 else "declining",
        "peak_season": int(seasons[np.argmax(values)]),
        "peak_value": round(float(np.max(values)), 4),
        "worst_season": int(seasons[np.argmin(values)]),
        "worst_value": round(float(np.min(values)), 4),
        "latest_value": round(float(values[-1]), 4),
        "career_avg": round(float(np.mean(values)), 4),
    }
