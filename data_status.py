#!/usr/bin/env python3
"""
데이터 업데이트 상태 모니터링 페이지
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from config import BATTER_STATS_FILE, PITCHER_STATS_FILE
from i18n import get_text

def show_data_status(lang="ko"):
    """데이터 상태 대시보드"""
    
    st.title("📊 " + get_text("data_status_title", lang))
    
    # 데이터 파일 존재 여부 확인
    batter_exists = os.path.exists(BATTER_STATS_FILE)
    pitcher_exists = os.path.exists(PITCHER_STATS_FILE)
    
    # 상태 표시
    col1, col2 = st.columns(2)
    
    with col1:
        if batter_exists:
            st.success("✅ 타자 데이터 파일 존재")
        else:
            st.error("❌ 타자 데이터 파일 없음")
    
    with col2:
        if pitcher_exists:
            st.success("✅ 투수 데이터 파일 존재")
        else:
            st.error("❌ 투수 데이터 파일 없음")
    
    if not (batter_exists and pitcher_exists):
        st.warning("⚠️ 데이터 파일이 없습니다. 데이터 업데이트를 실행해주세요.")
        st.code("python update_data.py")
        return
    
    # 데이터 로딩
    try:
        batter_df = pd.read_csv(BATTER_STATS_FILE)
        pitcher_df = pd.read_csv(PITCHER_STATS_FILE)
    except Exception as e:
        st.error(f"데이터 로딩 실패: {e}")
        return
    
    # 기본 통계 표시
    st.header("📈 데이터 개요")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="타자 레코드",
            value=f"{len(batter_df):,}개",
            delta=f"+{len(batter_df[batter_df['Season'] >= 2024])}" if len(batter_df[batter_df['Season'] >= 2024]) > 0 else None
        )
    
    with col2:
        st.metric(
            label="투수 레코드", 
            value=f"{len(pitcher_df):,}개",
            delta=f"+{len(pitcher_df[pitcher_df['Season'] >= 2024])}" if len(pitcher_df[pitcher_df['Season'] >= 2024]) > 0 else None
        )
    
    with col3:
        batter_seasons = f"{batter_df['Season'].min()} - {batter_df['Season'].max()}"
        st.metric(
            label="타자 데이터 기간",
            value=batter_seasons
        )
    
    with col4:
        pitcher_seasons = f"{pitcher_df['Season'].min()} - {pitcher_df['Season'].max()}"
        st.metric(
            label="투수 데이터 기간", 
            value=pitcher_seasons
        )
    
    # 시즌별 데이터 분포
    st.header("📊 시즌별 데이터 분포")
    
    # 타자 데이터 시즌별 분포
    batter_season_counts = batter_df['Season'].value_counts().sort_index()
    pitcher_season_counts = pitcher_df['Season'].value_counts().sort_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=batter_season_counts.index,
        y=batter_season_counts.values,
        mode='lines+markers',
        name='타자',
        line=dict(color='#1f77b4')
    ))
    fig.add_trace(go.Scatter(
        x=pitcher_season_counts.index,
        y=pitcher_season_counts.values,
        mode='lines+markers',
        name='투수',
        line=dict(color='#ff7f0e')
    ))
    
    fig.update_layout(
        title='시즌별 선수 데이터 수',
        xaxis_title='시즌',
        yaxis_title='선수 수',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 최신 데이터 하이라이트
    st.header("🏆 최신 시즌 하이라이트")
    
    latest_season = max(batter_df['Season'].max(), pitcher_df['Season'].max())
    
    if latest_season >= 2024:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⚾ 타자 하이라이트")
            recent_batters = batter_df[batter_df['Season'] == latest_season]
            
            if len(recent_batters) > 0:
                # 최고 타율
                top_avg = recent_batters.loc[recent_batters['BattingAverage'].idxmax()]
                st.write(f"**최고 타율**: {top_avg['PlayerName']} ({top_avg['BattingAverage']:.3f})")
                
                # 최다 홈런
                top_hr = recent_batters.loc[recent_batters['HomeRuns'].idxmax()]
                st.write(f"**최다 홈런**: {top_hr['PlayerName']} ({top_hr['HomeRuns']}개)")
                
                # 최다 타점
                top_rbi = recent_batters.loc[recent_batters['RBIs'].idxmax()]
                st.write(f"**최다 타점**: {top_rbi['PlayerName']} ({top_rbi['RBIs']}개)")
        
        with col2:
            st.subheader("🥎 투수 하이라이트")
            recent_pitchers = pitcher_df[pitcher_df['Season'] == latest_season]
            
            if len(recent_pitchers) > 0:
                # 최고 평균자책점 (최소 이닝 제한)
                qualified_pitchers = recent_pitchers[recent_pitchers['InningsPitched'] >= 50]
                if len(qualified_pitchers) > 0:
                    best_era = qualified_pitchers.loc[qualified_pitchers['EarnedRunAverage'].idxmin()]
                    st.write(f"**최고 평균자책점**: {best_era['PlayerName']} ({best_era['EarnedRunAverage']:.2f})")
                
                # 최다 승수
                top_wins = recent_pitchers.loc[recent_pitchers['Wins'].idxmax()]
                st.write(f"**최다 승수**: {top_wins['PlayerName']} ({top_wins['Wins']}승)")
                
                # 최다 탈삼진
                top_k = recent_pitchers.loc[recent_pitchers['StrikeOuts'].idxmax()]
                st.write(f"**최다 탈삼진**: {top_k['PlayerName']} ({top_k['StrikeOuts']}개)")
    
    # 데이터 품질 체크
    st.header("🔍 데이터 품질 체크")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("타자 데이터")
        
        # 결측치 확인
        batter_nulls = batter_df.isnull().sum()
        if batter_nulls.sum() > 0:
            st.warning(f"결측치 {batter_nulls.sum()}개 발견")
            st.write(batter_nulls[batter_nulls > 0])
        else:
            st.success("결측치 없음")
        
        # 중복 확인
        batter_duplicates = batter_df.duplicated(subset=['Season', 'PlayerID']).sum()
        if batter_duplicates > 0:
            st.warning(f"중복 레코드 {batter_duplicates}개 발견")
        else:
            st.success("중복 레코드 없음")
    
    with col2:
        st.subheader("투수 데이터")
        
        # 결측치 확인
        pitcher_nulls = pitcher_df.isnull().sum()
        if pitcher_nulls.sum() > 0:
            st.warning(f"결측치 {pitcher_nulls.sum()}개 발견")
            st.write(pitcher_nulls[pitcher_nulls > 0])
        else:
            st.success("결측치 없음")
        
        # 중복 확인
        pitcher_duplicates = pitcher_df.duplicated(subset=['Season', 'PlayerID']).sum()
        if pitcher_duplicates > 0:
            st.warning(f"중복 레코드 {pitcher_duplicates}개 발견")
        else:
            st.success("중복 레코드 없음")
    
    # 업데이트 가이드
    st.header("🔄 데이터 업데이트 가이드")
    
    st.write("최신 MLB 데이터를 업데이트하려면 다음 명령어를 사용하세요:")
    
    update_commands = [
        ("기본 업데이트 (2024년 이후)", "python update_data.py"),
        ("특정 연도 업데이트", "python update_data.py --start-year 2024 --end-year 2025"),
        ("백업과 함께 업데이트", "python update_data.py --backup"),
        ("PyBaseball 사용", "python update_data.py --method pybaseball"),
        ("MLB API 사용", "python update_data.py --method mlb-api")
    ]
    
    for description, command in update_commands:
        with st.expander(description):
            st.code(command, language="bash")
    
    # 자동 스케줄러 정보
    st.header("⏰ 자동 업데이트 스케줄러")
    
    st.write("정기적인 자동 업데이트를 위한 스케줄러:")
    
    scheduler_info = """
    **시즌 중 (3월-10월)**: 매일 오전 6시 자동 업데이트
    **시즌 외 (11월-2월)**: 매주 일요일 오전 8시 업데이트
    
    스케줄러 실행:
    ```bash
    # 일회성 업데이트
    python auto_update.py --mode once
    
    # 지속적인 자동 업데이트
    python auto_update.py --mode scheduler
    
    # 백그라운드 실행
    nohup python auto_update.py --mode scheduler > logs/scheduler.log 2>&1 &
    ```
    """
    
    st.markdown(scheduler_info)
    
    # 파일 정보
    st.header("📁 파일 정보")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if batter_exists:
            batter_stat = os.stat(BATTER_STATS_FILE)
            batter_size = batter_stat.st_size / (1024 * 1024)  # MB
            batter_modified = datetime.fromtimestamp(batter_stat.st_mtime)
            
            st.write("**타자 데이터 파일**")
            st.write(f"크기: {batter_size:.2f} MB")
            st.write(f"최종 수정: {batter_modified.strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col2:
        if pitcher_exists:
            pitcher_stat = os.stat(PITCHER_STATS_FILE)
            pitcher_size = pitcher_stat.st_size / (1024 * 1024)  # MB
            pitcher_modified = datetime.fromtimestamp(pitcher_stat.st_mtime)
            
            st.write("**투수 데이터 파일**")
            st.write(f"크기: {pitcher_size:.2f} MB")
            st.write(f"최종 수정: {pitcher_modified.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    show_data_status()
