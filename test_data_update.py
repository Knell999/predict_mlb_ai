#!/usr/bin/env python3
"""
데이터 업데이트 테스트 스크립트
새로운 데이터 수집 기능이 올바르게 작동하는지 테스트
"""

import sys
import os
import pandas as pd
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pybaseball():
    """PyBaseball 기능 테스트"""
    logger.info("=== PyBaseball 테스트 ===")
    
    try:
        from pybaseball_processor import PyBaseballDataProcessor
        processor = PyBaseballDataProcessor()
        
        # 2024년 데이터 소량 테스트
        logger.info("2024년 타자 데이터 수집 테스트...")
        batting_data = processor.collect_batting_data(2024, 2024)
        
        if not batting_data.empty:
            logger.info(f"✅ 타자 데이터 수집 성공: {len(batting_data)}개 레코드")
            logger.info(f"   컬럼: {list(batting_data.columns)}")
        else:
            logger.warning("⚠️ 타자 데이터가 비어있습니다")
        
        logger.info("2024년 투수 데이터 수집 테스트...")
        pitching_data = processor.collect_pitching_data(2024, 2024)
        
        if not pitching_data.empty:
            logger.info(f"✅ 투수 데이터 수집 성공: {len(pitching_data)}개 레코드")
            logger.info(f"   컬럼: {list(pitching_data.columns)}")
        else:
            logger.warning("⚠️ 투수 데이터가 비어있습니다")
        
        return True
        
    except ImportError:
        logger.error("❌ PyBaseball 라이브러리가 설치되지 않았습니다")
        logger.info("설치 명령: pip install pybaseball")
        return False
    except Exception as e:
        logger.error(f"❌ PyBaseball 테스트 실패: {e}")
        return False

def test_mlb_api():
    """MLB API 기능 테스트"""
    logger.info("=== MLB API 테스트 ===")
    
    try:
        from data_processor import MLBDataProcessor
        processor = MLBDataProcessor()
        
        # 팀 목록 조회 테스트
        logger.info("2024년 팀 목록 조회 테스트...")
        teams = processor.get_teams(2024)
        
        if teams:
            logger.info(f"✅ 팀 목록 조회 성공: {len(teams)}개 팀")
            logger.info(f"   첫 번째 팀: {teams[0].get('name', 'Unknown')}")
        else:
            logger.warning("⚠️ 팀 목록이 비어있습니다")
        
        # 첫 번째 팀의 로스터 조회 테스트
        if teams:
            first_team = teams[0]
            logger.info(f"{first_team['name']} 로스터 조회 테스트...")
            roster = processor.get_roster(first_team['id'], 2024)
            
            if roster:
                logger.info(f"✅ 로스터 조회 성공: {len(roster)}명")
            else:
                logger.warning("⚠️ 로스터가 비어있습니다")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ MLB API 테스트 실패: {e}")
        return False

def test_existing_data():
    """기존 데이터 파일 확인"""
    logger.info("=== 기존 데이터 확인 ===")
    
    try:
        from config import BATTER_STATS_FILE, PITCHER_STATS_FILE
        
        # 타자 데이터 확인
        if os.path.exists(BATTER_STATS_FILE):
            batter_df = pd.read_csv(BATTER_STATS_FILE)
            logger.info(f"✅ 타자 데이터 파일 존재: {len(batter_df)}개 레코드")
            logger.info(f"   시즌 범위: {batter_df['Season'].min()} - {batter_df['Season'].max()}")
            logger.info(f"   컬럼: {list(batter_df.columns)}")
        else:
            logger.warning(f"⚠️ 타자 데이터 파일 없음: {BATTER_STATS_FILE}")
        
        # 투수 데이터 확인
        if os.path.exists(PITCHER_STATS_FILE):
            pitcher_df = pd.read_csv(PITCHER_STATS_FILE)
            logger.info(f"✅ 투수 데이터 파일 존재: {len(pitcher_df)}개 레코드")
            logger.info(f"   시즌 범위: {pitcher_df['Season'].min()} - {pitcher_df['Season'].max()}")
            logger.info(f"   컬럼: {list(pitcher_df.columns)}")
        else:
            logger.warning(f"⚠️ 투수 데이터 파일 없음: {PITCHER_STATS_FILE}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 기존 데이터 확인 실패: {e}")
        return False

def test_update_script():
    """업데이트 스크립트 테스트"""
    logger.info("=== 업데이트 스크립트 테스트 ===")
    
    try:
        # update_data.py 스크립트 import 테스트
        import update_data
        logger.info("✅ update_data.py import 성공")
        
        # auto_update.py 스크립트 import 테스트
        import auto_update
        logger.info("✅ auto_update.py import 성공")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 업데이트 스크립트 테스트 실패: {e}")
        return False

def main():
    """전체 테스트 실행"""
    logger.info("🧪 MLB 데이터 업데이트 기능 테스트 시작")
    logger.info("=" * 50)
    
    tests = [
        ("기존 데이터 확인", test_existing_data),
        ("PyBaseball 기능", test_pybaseball),
        ("MLB API 기능", test_mlb_api),
        ("업데이트 스크립트", test_update_script)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 {test_name} 테스트 중...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} 테스트 중 오류: {e}")
            results[test_name] = False
    
    # 결과 요약
    logger.info("\n" + "=" * 50)
    logger.info("📊 테스트 결과 요약")
    logger.info("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 통과" if result else "❌ 실패"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n총 {passed}/{total}개 테스트 통과")
    
    if passed == total:
        logger.info("🎉 모든 테스트 통과! 데이터 업데이트 기능이 준비되었습니다.")
        
        logger.info("\n📋 다음 단계:")
        logger.info("1. PyBaseball 설치: pip install pybaseball")
        logger.info("2. 데이터 업데이트 실행: python update_data.py")
        logger.info("3. 자동 스케줄러 설정: python auto_update.py --mode scheduler")
        
    else:
        logger.warning("⚠️ 일부 테스트가 실패했습니다. 문제를 해결한 후 다시 시도하세요.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
