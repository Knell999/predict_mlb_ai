"""
자동화된 MLB 데이터 업데이트 스케줄러
정기적으로 데이터를 업데이트하는 스크립트
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
import os
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def is_season_active():
    """MLB 시즌이 활성화되어 있는지 확인"""
    now = datetime.now()
    # 일반적으로 MLB 시즌은 3월~10월
    return 3 <= now.month <= 10

def update_data_job():
    """스케줄된 데이터 업데이트 작업"""
    logger.info("스케줄된 데이터 업데이트 시작")
    
    try:
        # 현재 연도 데이터만 업데이트
        current_year = datetime.now().year
        
        # PyBaseball 먼저 시도
        try:
            from pybaseball_processor import PyBaseballDataProcessor
            processor = PyBaseballDataProcessor()
            processor.update_data(start_year=current_year, end_year=current_year)
            logger.info("PyBaseball을 사용한 데이터 업데이트 성공")
            return True
        except Exception as e:
            logger.warning(f"PyBaseball 업데이트 실패: {e}")
        
        # MLB API 시도
        try:
            from data_processor import MLBDataProcessor
            processor = MLBDataProcessor()
            processor.update_data(start_year=current_year, end_year=current_year)
            logger.info("MLB API를 사용한 데이터 업데이트 성공")
            return True
        except Exception as e:
            logger.error(f"MLB API 업데이트도 실패: {e}")
            return False
            
    except Exception as e:
        logger.error(f"데이터 업데이트 중 예상치 못한 오류: {e}")
        return False

def daily_update():
    """일일 업데이트 (시즌 중에만)"""
    if is_season_active():
        logger.info("시즌 중이므로 일일 업데이트 실행")
        update_data_job()
    else:
        logger.info("시즌 외 기간이므로 일일 업데이트 건너뜀")

def weekly_update():
    """주간 업데이트 (시즌 외에도 실행)"""
    logger.info("주간 업데이트 실행")
    update_data_job()

def setup_scheduler():
    """스케줄러 설정"""
    # 시즌 중 매일 오전 6시에 업데이트
    schedule.every().day.at("06:00").do(daily_update)
    
    # 시즌 외에도 매주 일요일 오전 8시에 업데이트
    schedule.every().sunday.at("08:00").do(weekly_update)
    
    logger.info("스케줄러 설정 완료:")
    logger.info("- 시즌 중: 매일 오전 6시")
    logger.info("- 시즌 외: 매주 일요일 오전 8시")

def run_scheduler():
    """스케줄러 실행"""
    setup_scheduler()
    
    logger.info("데이터 업데이트 스케줄러 시작")
    logger.info("중지하려면 Ctrl+C를 누르세요")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
    except KeyboardInterrupt:
        logger.info("스케줄러 종료")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MLB 데이터 자동 업데이트 스케줄러')
    parser.add_argument(
        '--mode',
        choices=['scheduler', 'once'],
        default='once',
        help='실행 모드: scheduler (지속 실행) 또는 once (한 번만 실행)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'scheduler':
        run_scheduler()
    else:
        logger.info("일회성 데이터 업데이트 실행")
        success = update_data_job()
        if success:
            logger.info("데이터 업데이트 완료")
        else:
            logger.error("데이터 업데이트 실패")
            sys.exit(1)

if __name__ == "__main__":
    main()
