#!/usr/bin/env python3
"""
MLB 데이터 품질 검증 도구
수집된 데이터의 무결성과 품질을 검증합니다.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any
from config import BATTER_STATS_FILE, PITCHER_STATS_FILE

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataQualityChecker:
    """데이터 품질 검증 클래스"""
    
    def __init__(self):
        self.batter_file = BATTER_STATS_FILE
        self.pitcher_file = PITCHER_STATS_FILE
        
        # 예상 컬럼 정의
        self.expected_batter_columns = [
            'Season', 'PlayerID', 'PlayerName', 'Team', 'GamesPlayed', 
            'AtBats', 'Runs', 'Hits', 'HomeRuns', 'RBIs', 'StolenBases', 
            'Walks', 'StrikeOuts', 'BattingAverage', 'OnBasePercentage', 
            'SluggingPercentage', 'OPS'
        ]
        
        self.expected_pitcher_columns = [
            'Season', 'PlayerID', 'PlayerName', 'Team', 'GamesPlayed',
            'Wins', 'Losses', 'EarnedRunAverage', 'InningsPitched',
            'StrikeOuts', 'Walks', 'HitsAllowed', 'HomeRunsAllowed',
            'Saves', 'Whip', 'QualifyingInnings'
        ]
        
        # 통계적 범위 (정상 범위)
        self.batter_ranges = {
            'BattingAverage': (0.0, 1.0),
            'OnBasePercentage': (0.0, 1.0),
            'SluggingPercentage': (0.0, 4.0),
            'OPS': (0.0, 5.0),
            'HomeRuns': (0, 100),
            'RBIs': (0, 200),
            'StolenBases': (0, 150)
        }
        
        self.pitcher_ranges = {
            'EarnedRunAverage': (0.0, 15.0),
            'Whip': (0.0, 5.0),
            'Wins': (0, 30),
            'Losses': (0, 30),
            'Saves': (0, 70),
            'InningsPitched': (0, 300)
        }
    
    def check_file_existence(self) -> Dict[str, bool]:
        """파일 존재 여부 확인"""
        import os
        
        result = {
            'batter_file_exists': os.path.exists(self.batter_file),
            'pitcher_file_exists': os.path.exists(self.pitcher_file)
        }
        
        logger.info(f"파일 존재 확인: {result}")
        return result
    
    def check_data_structure(self) -> Dict[str, Any]:
        """데이터 구조 검증"""
        result = {}
        
        try:
            # 타자 데이터 검증
            batter_df = pd.read_csv(self.batter_file)
            result['batter'] = {
                'total_records': len(batter_df),
                'columns': list(batter_df.columns),
                'missing_columns': [col for col in self.expected_batter_columns 
                                  if col not in batter_df.columns],
                'extra_columns': [col for col in batter_df.columns 
                                if col not in self.expected_batter_columns],
                'season_range': (batter_df['Season'].min(), batter_df['Season'].max()),
                'null_counts': batter_df.isnull().sum().to_dict()
            }
            
            # 투수 데이터 검증
            pitcher_df = pd.read_csv(self.pitcher_file)
            result['pitcher'] = {
                'total_records': len(pitcher_df),
                'columns': list(pitcher_df.columns),
                'missing_columns': [col for col in self.expected_pitcher_columns 
                                  if col not in pitcher_df.columns],
                'extra_columns': [col for col in pitcher_df.columns 
                                if col not in self.expected_pitcher_columns],
                'season_range': (pitcher_df['Season'].min(), pitcher_df['Season'].max()),
                'null_counts': pitcher_df.isnull().sum().to_dict()
            }
            
        except Exception as e:
            logger.error(f"데이터 구조 검증 실패: {e}")
            result['error'] = str(e)
        
        return result
    
    def check_data_quality(self) -> Dict[str, Any]:
        """데이터 품질 검증"""
        result = {}
        
        try:
            # 타자 데이터 품질 검증
            batter_df = pd.read_csv(self.batter_file)
            batter_issues = []
            
            # 중복 레코드 검사
            duplicates = batter_df.duplicated(subset=['Season', 'PlayerID']).sum()
            if duplicates > 0:
                batter_issues.append(f"중복 레코드 {duplicates}개 발견")
            
            # 통계 범위 검사
            for col, (min_val, max_val) in self.batter_ranges.items():
                if col in batter_df.columns:
                    outliers = ((batter_df[col] < min_val) | (batter_df[col] > max_val)).sum()
                    if outliers > 0:
                        batter_issues.append(f"{col}: {outliers}개 이상치 발견")
            
            # 논리적 일관성 검사
            if 'AtBats' in batter_df.columns and 'Hits' in batter_df.columns:
                impossible_hits = (batter_df['Hits'] > batter_df['AtBats']).sum()
                if impossible_hits > 0:
                    batter_issues.append(f"타수보다 안타가 많은 레코드 {impossible_hits}개")
            
            result['batter'] = {
                'issues': batter_issues,
                'quality_score': max(0, 100 - len(batter_issues) * 10)
            }
            
            # 투수 데이터 품질 검증
            pitcher_df = pd.read_csv(self.pitcher_file)
            pitcher_issues = []
            
            # 중복 레코드 검사
            duplicates = pitcher_df.duplicated(subset=['Season', 'PlayerID']).sum()
            if duplicates > 0:
                pitcher_issues.append(f"중복 레코드 {duplicates}개 발견")
            
            # 통계 범위 검사
            for col, (min_val, max_val) in self.pitcher_ranges.items():
                if col in pitcher_df.columns:
                    outliers = ((pitcher_df[col] < min_val) | (pitcher_df[col] > max_val)).sum()
                    if outliers > 0:
                        pitcher_issues.append(f"{col}: {outliers}개 이상치 발견")
            
            # 논리적 일관성 검사
            if 'Wins' in pitcher_df.columns and 'Losses' in pitcher_df.columns:
                total_decisions = pitcher_df['Wins'] + pitcher_df['Losses']
                if 'GamesPlayed' in pitcher_df.columns:
                    impossible_decisions = (total_decisions > pitcher_df['GamesPlayed']).sum()
                    if impossible_decisions > 0:
                        pitcher_issues.append(f"경기수보다 승부가 많은 레코드 {impossible_decisions}개")
            
            result['pitcher'] = {
                'issues': pitcher_issues,
                'quality_score': max(0, 100 - len(pitcher_issues) * 10)
            }
            
        except Exception as e:
            logger.error(f"데이터 품질 검증 실패: {e}")
            result['error'] = str(e)
        
        return result
    
    def get_season_statistics(self) -> Dict[str, Any]:
        """시즌별 통계 요약"""
        result = {}
        
        try:
            # 타자 데이터 시즌별 통계
            batter_df = pd.read_csv(self.batter_file)
            batter_season_stats = batter_df.groupby('Season').agg({
                'PlayerID': 'count',
                'BattingAverage': ['mean', 'std'],
                'HomeRuns': ['mean', 'max'],
                'RBIs': ['mean', 'max']
            }).round(3)
            
            result['batter_by_season'] = batter_season_stats.to_dict()
            
            # 투수 데이터 시즌별 통계
            pitcher_df = pd.read_csv(self.pitcher_file)
            pitcher_season_stats = pitcher_df.groupby('Season').agg({
                'PlayerID': 'count',
                'EarnedRunAverage': ['mean', 'std'],
                'Wins': ['mean', 'max'],
                'StrikeOuts': ['mean', 'max']
            }).round(3)
            
            result['pitcher_by_season'] = pitcher_season_stats.to_dict()
            
            # 최신 시즌 하이라이트
            latest_season = max(batter_df['Season'].max(), pitcher_df['Season'].max())
            result['latest_season'] = latest_season
            
            if latest_season in batter_df['Season'].values:
                latest_batters = batter_df[batter_df['Season'] == latest_season]
                result['latest_batter_highlights'] = {
                    'total_players': len(latest_batters),
                    'top_avg': latest_batters.nlargest(1, 'BattingAverage')[['PlayerName', 'BattingAverage']].to_dict('records'),
                    'top_hr': latest_batters.nlargest(1, 'HomeRuns')[['PlayerName', 'HomeRuns']].to_dict('records')
                }
            
            if latest_season in pitcher_df['Season'].values:
                latest_pitchers = pitcher_df[pitcher_df['Season'] == latest_season]
                result['latest_pitcher_highlights'] = {
                    'total_players': len(latest_pitchers),
                    'best_era': latest_pitchers.nsmallest(1, 'EarnedRunAverage')[['PlayerName', 'EarnedRunAverage']].to_dict('records'),
                    'top_wins': latest_pitchers.nlargest(1, 'Wins')[['PlayerName', 'Wins']].to_dict('records')
                }
            
        except Exception as e:
            logger.error(f"시즌별 통계 생성 실패: {e}")
            result['error'] = str(e)
        
        return result
    
    def generate_report(self) -> Dict[str, Any]:
        """종합 품질 보고서 생성"""
        logger.info("데이터 품질 검증 시작...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'file_check': self.check_file_existence(),
            'structure_check': self.check_data_structure(),
            'quality_check': self.check_data_quality(),
            'season_statistics': self.get_season_statistics()
        }
        
        # 전체 품질 점수 계산
        quality_scores = []
        if 'batter' in report['quality_check']:
            quality_scores.append(report['quality_check']['batter']['quality_score'])
        if 'pitcher' in report['quality_check']:
            quality_scores.append(report['quality_check']['pitcher']['quality_score'])
        
        if quality_scores:
            report['overall_quality_score'] = sum(quality_scores) / len(quality_scores)
        else:
            report['overall_quality_score'] = 0
        
        logger.info(f"데이터 품질 검증 완료. 전체 점수: {report['overall_quality_score']:.1f}/100")
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """품질 보고서 요약 출력"""
        print("\n" + "="*60)
        print("📊 MLB 데이터 품질 검증 보고서")
        print("="*60)
        
        print(f"🕐 검증 시간: {report['timestamp']}")
        print(f"📈 전체 품질 점수: {report['overall_quality_score']:.1f}/100")
        
        # 파일 존재 여부
        print("\n📁 파일 확인:")
        file_check = report['file_check']
        print(f"  타자 데이터: {'✅' if file_check['batter_file_exists'] else '❌'}")
        print(f"  투수 데이터: {'✅' if file_check['pitcher_file_exists'] else '❌'}")
        
        # 데이터 구조
        if 'structure_check' in report:
            structure = report['structure_check']
            if 'batter' in structure:
                batter = structure['batter']
                print(f"\n⚾ 타자 데이터:")
                print(f"  레코드 수: {batter['total_records']:,}개")
                print(f"  시즌 범위: {batter['season_range'][0]} - {batter['season_range'][1]}")
                if batter['missing_columns']:
                    print(f"  누락 컬럼: {batter['missing_columns']}")
            
            if 'pitcher' in structure:
                pitcher = structure['pitcher']
                print(f"\n🥎 투수 데이터:")
                print(f"  레코드 수: {pitcher['total_records']:,}개")
                print(f"  시즌 범위: {pitcher['season_range'][0]} - {pitcher['season_range'][1]}")
                if pitcher['missing_columns']:
                    print(f"  누락 컬럼: {pitcher['missing_columns']}")
        
        # 품질 이슈
        if 'quality_check' in report:
            quality = report['quality_check']
            if 'batter' in quality and quality['batter']['issues']:
                print(f"\n⚠️ 타자 데이터 이슈:")
                for issue in quality['batter']['issues']:
                    print(f"  - {issue}")
            
            if 'pitcher' in quality and quality['pitcher']['issues']:
                print(f"\n⚠️ 투수 데이터 이슈:")
                for issue in quality['pitcher']['issues']:
                    print(f"  - {issue}")
        
        # 최신 시즌 하이라이트
        if 'season_statistics' in report:
            stats = report['season_statistics']
            if 'latest_season' in stats:
                print(f"\n🏆 {stats['latest_season']} 시즌 하이라이트:")
                
                if 'latest_batter_highlights' in stats:
                    batter_hl = stats['latest_batter_highlights']
                    print(f"  타자 선수 수: {batter_hl['total_players']}명")
                    if batter_hl['top_avg']:
                        top_avg = batter_hl['top_avg'][0]
                        print(f"  최고 타율: {top_avg['PlayerName']} ({top_avg['BattingAverage']:.3f})")
                    if batter_hl['top_hr']:
                        top_hr = batter_hl['top_hr'][0]
                        print(f"  최다 홈런: {top_hr['PlayerName']} ({top_hr['HomeRuns']}개)")
                
                if 'latest_pitcher_highlights' in stats:
                    pitcher_hl = stats['latest_pitcher_highlights']
                    print(f"  투수 선수 수: {pitcher_hl['total_players']}명")
                    if pitcher_hl['best_era']:
                        best_era = pitcher_hl['best_era'][0]
                        print(f"  최고 평균자책점: {best_era['PlayerName']} ({best_era['EarnedRunAverage']:.2f})")
                    if pitcher_hl['top_wins']:
                        top_wins = pitcher_hl['top_wins'][0]
                        print(f"  최다 승수: {top_wins['PlayerName']} ({top_wins['Wins']}승)")
        
        print("\n" + "="*60)

def main():
    """메인 실행 함수"""
    checker = DataQualityChecker()
    report = checker.generate_report()
    checker.print_summary(report)
    
    # JSON 형태로도 저장
    import json
    report_file = f"data_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 상세 보고서가 {report_file}에 저장되었습니다.")

if __name__ == "__main__":
    main()
