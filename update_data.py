#!/usr/bin/env python3
"""
MLB 데이터 업데이트 스크립트
간편하게 최신 데이터를 수집하고 업데이트할 수 있는 스크립트
"""

import argparse
import sys
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_with_pybaseball(start_year, end_year):
    """PyBaseball을 사용한 데이터 업데이트"""
    try:
        from pybaseball_processor import PyBaseballDataProcessor
        processor = PyBaseballDataProcessor()
        processor.update_data(start_year, end_year)
        return True
    except ImportError:
        logger.error("pybaseball 라이브러리가 설치되지 않았습니다.")
        logger.info("설치 명령: pip install pybaseball")
        return False
    except Exception as e:
        logger.error(f"PyBaseball 업데이트 실패: {e}")
        return False

def update_with_mlb_api(start_year, end_year):
    """MLB 공식 API를 사용한 데이터 업데이트"""
    try:
        from data_processor import MLBDataProcessor
        processor = MLBDataProcessor()
        processor.update_data(start_year, end_year)
        return True
    except Exception as e:
        logger.error(f"MLB API 업데이트 실패: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='MLB 데이터 업데이트 스크립트')
    parser.add_argument(
        '--method', 
        choices=['pybaseball', 'mlb-api', 'auto'], 
        default='auto',
        help='데이터 수집 방법 선택 (기본값: auto)'
    )
    parser.add_argument(
        '--start-year', 
        type=int, 
        default=2024,
        help='시작 연도 (기본값: 2024)'
    )
    parser.add_argument(
        '--end-year', 
        type=int, 
        default=datetime.now().year,
        help='종료 연도 (기본값: 현재 연도)'
    )
    parser.add_argument(
        '--backup', 
        action='store_true',
        help='기존 데이터 백업 생성'
    )
    
    args = parser.parse_args()
    
    logger.info(f"MLB 데이터 업데이트 시작")
    logger.info(f"기간: {args.start_year} - {args.end_year}")
    logger.info(f"방법: {args.method}")
    
    # 백업 생성
    if args.backup:
        logger.info("기존 데이터 백업 생성...")
        import shutil
        import os
        from config import BATTER_STATS_FILE, PITCHER_STATS_FILE
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if os.path.exists(BATTER_STATS_FILE):
            backup_file = BATTER_STATS_FILE.replace('.csv', f'_backup_{timestamp}.csv')
            shutil.copy2(BATTER_STATS_FILE, backup_file)
            logger.info(f"타자 데이터 백업: {backup_file}")
        
        if os.path.exists(PITCHER_STATS_FILE):
            backup_file = PITCHER_STATS_FILE.replace('.csv', f'_backup_{timestamp}.csv')
            shutil.copy2(PITCHER_STATS_FILE, backup_file)
            logger.info(f"투수 데이터 백업: {backup_file}")
    
    # 데이터 업데이트 실행
    success = False
    
    if args.method == 'pybaseball':
        success = update_with_pybaseball(args.start_year, args.end_year)
    elif args.method == 'mlb-api':
        success = update_with_mlb_api(args.start_year, args.end_year)
    elif args.method == 'auto':
        # PyBaseball 먼저 시도, 실패하면 MLB API 사용
        logger.info("PyBaseball 방법 시도...")
        success = update_with_pybaseball(args.start_year, args.end_year)
        
        if not success:
            logger.info("MLB 공식 API 방법 시도...")
            success = update_with_mlb_api(args.start_year, args.end_year)
    
    if success:
        logger.info("데이터 업데이트 성공!")
        
        # 간단한 통계 출력
        try:
            import pandas as pd
            import os
            from config import BATTER_STATS_FILE, PITCHER_STATS_FILE
            
            if os.path.exists(BATTER_STATS_FILE):
                batter_df = pd.read_csv(BATTER_STATS_FILE)
                logger.info(f"타자 데이터: {len(batter_df)}개 레코드")
                logger.info(f"시즌 범위: {batter_df['Season'].min()} - {batter_df['Season'].max()}")
            
            if os.path.exists(PITCHER_STATS_FILE):
                pitcher_df = pd.read_csv(PITCHER_STATS_FILE)
                logger.info(f"투수 데이터: {len(pitcher_df)}개 레코드")
                logger.info(f"시즌 범위: {pitcher_df['Season'].min()} - {pitcher_df['Season'].max()}")
                
        except Exception as e:
            logger.warning(f"통계 출력 실패: {e}")
        
    else:
        logger.error("모든 데이터 업데이트 방법이 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()
