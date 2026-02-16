"""
유사 선수 검색 도구
유클리드 거리 기반 정규화 유사도 계산을 제공합니다.
"""

import sys
import os
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@tool
def find_similar_players(
    player_name: str,
    player_type: str,
    metrics: List[str],
    season: Optional[int] = None,
    top_n: int = 10,
) -> List[Dict[str, Any]]:
    """특정 선수와 통계적으로 유사한 선수를 찾습니다.

    정규화된 지표에 대해 유클리드 거리를 계산하여 가장 유사한 선수를 반환합니다.

    Args:
        player_name: 기준 선수 이름
        player_type: "batter" 또는 "pitcher"
        metrics: 비교에 사용할 지표 목록
        season: 특정 시즌 (None이면 커리어 평균)
        top_n: 반환할 유사 선수 수 (기본 10)

    Returns:
        유사 선수 목록 (거리 점수, 지표값 포함)
    """
    from utils import load_data, load_pitcher_data

    df = load_data() if player_type == "batter" else load_pitcher_data()
    valid_metrics = [m for m in metrics if m in df.columns]
    if not valid_metrics:
        return [{"error": "유효한 지표가 없습니다"}]

    if season:
        df = df[df['Season'] == season]

    player_avgs = df.groupby('PlayerName')[valid_metrics].mean()

    if player_name not in player_avgs.index:
        return [{"error": f"선수 '{player_name}'을(를) 찾을 수 없습니다"}]

    target = player_avgs.loc[player_name].values

    means = player_avgs.mean()
    stds = player_avgs.std()
    stds = stds.replace(0, 1)
    normalized = (player_avgs - means) / stds
    target_norm = (target - means.values) / stds.values

    distances = np.sqrt(((normalized.values - target_norm) ** 2).sum(axis=1))
    player_avgs = player_avgs.copy()
    player_avgs['distance'] = distances

    similar = player_avgs.drop(index=player_name, errors='ignore')
    similar = similar.nsmallest(top_n, 'distance')

    results = []
    for name, row in similar.iterrows():
        entry = {
            "player_name": name,
            "distance": round(float(row['distance']), 4),
        }
        for m in valid_metrics:
            entry[m] = round(float(row[m]), 4)
        results.append(entry)

    return results


@tool
def find_players_by_criteria(
    player_type: str,
    criteria: Dict[str, Dict[str, float]],
    season: Optional[int] = None,
    top_n: int = 10,
) -> List[Dict[str, Any]]:
    """통계 조건에 맞는 선수를 검색합니다.

    Args:
        player_type: "batter" 또는 "pitcher"
        criteria: 지표별 범위 딕셔너리, 예: {"BattingAverage": {"min": 0.300}}
        season: 특정 시즌 필터 (None이면 전체)
        top_n: 최대 반환 결과 수

    Returns:
        조건에 맞는 선수 목록
    """
    from utils import load_data, load_pitcher_data

    df = load_data() if player_type == "batter" else load_pitcher_data()

    if season:
        df = df[df['Season'] == season]

    mask = pd.Series(True, index=df.index)
    valid_criteria_keys = []
    for metric, bounds in criteria.items():
        if metric not in df.columns:
            continue
        valid_criteria_keys.append(metric)
        if "min" in bounds:
            mask &= df[metric] >= bounds["min"]
        if "max" in bounds:
            mask &= df[metric] <= bounds["max"]

    result_df = df[mask].head(top_n)
    columns = ['PlayerName', 'Season'] + valid_criteria_keys
    columns = [c for c in columns if c in result_df.columns]

    return result_df[columns].to_dict(orient="records")
