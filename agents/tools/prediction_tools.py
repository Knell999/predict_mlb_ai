"""
예측 도구
Prophet 모델을 Agent Tool로 래핑합니다.
"""

import sys
import os
from typing import Dict, Any
from langchain_core.tools import tool
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@tool
def run_prophet_forecast(
    player_name: str, player_type: str, metric: str, periods: int = 5
) -> Dict[str, Any]:
    """Prophet 시계열 모델로 선수의 특정 지표를 예측합니다.

    Args:
        player_name: 선수 이름
        player_type: "batter" 또는 "pitcher"
        metric: 예측할 지표 컬럼명
        periods: 예측 연도 수 (기본 5)

    Returns:
        예측 결과 (예측값, 신뢰 구간 포함)
    """
    from utils import load_data, load_pitcher_data
    from predict import get_prophet_forecast

    df = load_data() if player_type == "batter" else load_pitcher_data()
    player_data = df[df['PlayerName'] == player_name].copy()

    if player_data.empty:
        return {"error": f"선수를 찾을 수 없습니다: {player_name}"}
    if len(player_data) < 3:
        return {"error": f"데이터 부족: {len(player_data)}시즌 (최소 3시즌 필요)"}
    if metric not in player_data.columns:
        return {"error": f"지표를 찾을 수 없습니다: {metric}"}

    player_data['Season'] = pd.to_datetime(player_data['Season'], format='%Y')
    forecast = get_prophet_forecast(player_data, metric, periods=periods)

    if forecast is None:
        return {"error": "Prophet 예측에 실패했습니다"}

    player_metric = player_data[['Season', metric]].copy()
    player_metric.columns = ['ds', 'y']
    future_forecast = forecast[forecast['ds'] > player_metric['ds'].max()]

    return {
        "player_name": player_name,
        "metric": metric,
        "periods": periods,
        "historical_seasons": len(player_data),
        "predictions": [
            {
                "year": int(row['ds'].year),
                "predicted": round(float(row['yhat']), 4),
                "lower_bound": round(float(row['yhat_lower']), 4),
                "upper_bound": round(float(row['yhat_upper']), 4),
            }
            for _, row in future_forecast.iterrows()
        ],
        "trend": (
            "improving"
            if future_forecast['yhat'].iloc[-1] > float(player_metric['y'].iloc[-1])
            else "declining"
        ),
    }


@tool
def assess_prediction_data_adequacy(
    player_name: str, player_type: str
) -> Dict[str, Any]:
    """선수의 예측 데이터 충분성을 평가합니다.

    Args:
        player_name: 선수 이름
        player_type: "batter" 또는 "pitcher"

    Returns:
        데이터 충분성 평가 결과 (시즌 수, 최근 데이터 여부, 갭 등)
    """
    from utils import load_data, load_pitcher_data

    df = load_data() if player_type == "batter" else load_pitcher_data()
    player_data = df[df['PlayerName'] == player_name].sort_values('Season')

    if player_data.empty:
        return {"adequate": False, "reason": "선수를 찾을 수 없습니다"}

    seasons = sorted(player_data['Season'].tolist())
    seasons_int = [int(s) for s in seasons]
    gaps = [seasons_int[i + 1] - seasons_int[i] for i in range(len(seasons_int) - 1)]

    total = len(seasons_int)
    confidence = "high" if total >= 8 else "medium" if total >= 5 else "low"

    return {
        "player_name": player_name,
        "total_seasons": total,
        "season_range": [seasons_int[0], seasons_int[-1]],
        "has_recent_data": seasons_int[-1] >= 2023,
        "season_gaps": gaps,
        "max_gap": max(gaps) if gaps else 0,
        "adequate": total >= 3,
        "confidence_level": confidence,
    }
