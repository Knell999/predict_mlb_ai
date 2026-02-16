"""
데이터 품질 검증 도구
data_quality_checker.py를 Agent Tool로 래핑합니다.
"""

import sys
import os
from typing import Dict, Any, List
from langchain_core.tools import tool
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@tool
def check_file_existence() -> Dict[str, bool]:
    """타자/투수 데이터 파일의 존재 여부를 확인합니다."""
    from data_quality_checker import DataQualityChecker
    checker = DataQualityChecker()
    return checker.check_file_existence()


@tool
def check_data_structure() -> Dict[str, Any]:
    """데이터 파일 구조를 검증합니다 (컬럼, 레코드 수, 시즌 범위, null 수)."""
    from data_quality_checker import DataQualityChecker
    checker = DataQualityChecker()
    return checker.check_data_structure()


@tool
def check_data_quality() -> Dict[str, Any]:
    """데이터 품질을 검사합니다 (중복, 범위 위반, 논리 일관성)."""
    from data_quality_checker import DataQualityChecker
    checker = DataQualityChecker()
    return checker.check_data_quality()


@tool
def get_season_statistics() -> Dict[str, Any]:
    """시즌별 집계 통계와 최근 시즌 하이라이트를 조회합니다."""
    from data_quality_checker import DataQualityChecker
    checker = DataQualityChecker()
    return checker.get_season_statistics()


@tool
def detect_statistical_anomalies(
    player_type: str, z_threshold: float = 3.0
) -> List[Dict[str, Any]]:
    """Z-score 방법으로 통계적 이상치를 탐지합니다.

    Args:
        player_type: "batter" 또는 "pitcher"
        z_threshold: 이상치 판별 Z-score 임계값 (기본 3.0)

    Returns:
        이상치 레코드 목록 (선수, 시즌, 지표, 값, z-score)
    """
    from config import (
        BATTER_STATS_FILE, PITCHER_STATS_FILE,
        BATTING_METRICS, PITCHING_METRICS,
    )

    file_path = BATTER_STATS_FILE if player_type == "batter" else PITCHER_STATS_FILE
    metrics = BATTING_METRICS if player_type == "batter" else PITCHING_METRICS

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return [{"error": f"데이터 파일을 찾을 수 없습니다: {file_path}"}]

    anomalies = []
    for metric in metrics:
        if metric not in df.columns:
            continue
        col = df[metric].dropna()
        if col.empty:
            continue
        mean_val = col.mean()
        std_val = col.std()
        if std_val == 0:
            continue

        z_scores = (df[metric] - mean_val) / std_val
        outlier_mask = z_scores.abs() > z_threshold

        for idx in df[outlier_mask].index:
            row = df.loc[idx]
            anomalies.append({
                "player_name": row.get('PlayerName', 'Unknown'),
                "season": int(row.get('Season', 0)),
                "metric": metric,
                "value": round(float(row[metric]), 4),
                "z_score": round(float(z_scores[idx]), 2),
                "league_mean": round(float(mean_val), 4),
                "league_std": round(float(std_val), 4),
            })

    return anomalies
