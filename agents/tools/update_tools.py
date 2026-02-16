"""
데이터 업데이트 도구
update_data.py를 Agent Tool로 래핑합니다.
"""

import sys
import os
import shutil
from datetime import datetime
from typing import Dict, Any
from langchain_core.tools import tool
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@tool
def run_pybaseball_update(start_year: int, end_year: int) -> Dict[str, Any]:
    """PyBaseball 라이브러리를 사용하여 데이터를 업데이트합니다.

    Args:
        start_year: 수집 시작 연도
        end_year: 수집 종료 연도

    Returns:
        성공 여부와 레코드 수
    """
    try:
        from pybaseball_processor import PyBaseballDataProcessor
        processor = PyBaseballDataProcessor()
        processor.update_data(start_year, end_year)
        return {
            "success": True,
            "method": "pybaseball",
            "start_year": start_year,
            "end_year": end_year,
        }
    except Exception as e:
        return {"success": False, "method": "pybaseball", "error": str(e)}


@tool
def run_mlb_api_update(start_year: int, end_year: int) -> Dict[str, Any]:
    """MLB 공식 Stats API를 사용하여 데이터를 업데이트합니다.

    Args:
        start_year: 수집 시작 연도
        end_year: 수집 종료 연도

    Returns:
        성공 여부와 레코드 수
    """
    try:
        from data_processor import MLBDataProcessor
        processor = MLBDataProcessor()
        processor.update_data(start_year, end_year)
        return {
            "success": True,
            "method": "mlb-api",
            "start_year": start_year,
            "end_year": end_year,
        }
    except Exception as e:
        return {"success": False, "method": "mlb-api", "error": str(e)}


@tool
def create_data_backup() -> Dict[str, Any]:
    """현재 데이터 파일의 타임스탬프 백업을 생성합니다."""
    from config import BATTER_STATS_FILE, PITCHER_STATS_FILE

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backed_up = []

    for filepath, label in [(BATTER_STATS_FILE, "batter"), (PITCHER_STATS_FILE, "pitcher")]:
        if os.path.exists(filepath):
            backup = filepath.replace('.csv', f'_backup_{timestamp}.csv')
            shutil.copy2(filepath, backup)
            backed_up.append({"file": label, "backup_path": backup})

    return {"timestamp": timestamp, "backups": backed_up}


@tool
def get_current_data_stats() -> Dict[str, Any]:
    """현재 데이터 파일의 통계를 조회합니다 (레코드 수, 시즌 범위, 파일 크기)."""
    from config import BATTER_STATS_FILE, PITCHER_STATS_FILE

    result = {}
    for filepath, label in [(BATTER_STATS_FILE, "batter"), (PITCHER_STATS_FILE, "pitcher")]:
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            stat = os.stat(filepath)
            result[label] = {
                "records": len(df),
                "season_range": [int(df['Season'].min()), int(df['Season'].max())],
                "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
            }
        else:
            result[label] = {"error": "파일을 찾을 수 없습니다"}
    return result
