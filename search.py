import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
from streamlit_option_menu import option_menu
from utils import load_data, load_pitcher_data
from matplotlib.ticker import MaxNLocator
from i18n import get_text

path = 'font/H2GTRM.TTF'
fontprop = fm.FontProperties(fname=path, size=12)

df = load_data()
df_pitchers = load_pitcher_data()

# 리그 평균 계산 함수 추가
def calculate_league_averages(df, metrics):
    """
    시즌별 리그 평균을 계산하는 함수입니다.
    
    Args:
        df: 분석할 데이터프레임
        metrics: 계산할 지표들의 리스트
        
    Returns:
        시즌별로 그룹화된 리그 평균 데이터프레임
    """
    league_averages = df.groupby('Season')[metrics].mean().reset_index()
    return league_averages

# 타자와 투수의 리그 평균 계산
batting_metrics = ['BattingAverage', 'OnBasePercentage', 'SluggingPercentage', 'OPS', 'Hits', 'RBIs', 'HomeRuns', 'StolenBases', 'Walks', 'StrikeOuts']
pitching_metrics = ['EarnedRunAverage', 'Whip', 'Wins', 'Losses', 'StrikeOuts', 'InningsPitched', 'Walks', 'HitsAllowed']

batting_league_avg = calculate_league_averages(df, batting_metrics)
pitching_league_avg = calculate_league_averages(df_pitchers, pitching_metrics)

def run_search(lang="ko"):
    """MLB 선수 기록을 조회하고 시각화하는 함수입니다."""
    st.title(get_text("search_title", lang))

    menu_options = {
        'ko': ['타자(선수기준)', '타자(시즌기준)', '투수(선수기준)', '투수(시즌기준)'],
        'en': ['Batters (By Player)', 'Batters (By Season)', 'Pitchers (By Player)', 'Pitchers (By Season)'],
        'ja': ['打者(選手基準)', '打者(シーズン基準)', '投手(選手基準)', '投手(シーズン基準)']
    }
    
    selected_lang_options = menu_options.get(lang, menu_options['ko'])
    
    selected = option_menu(
        None,
        selected_lang_options,
        icons=['person-fill', 'calendar-date', 'person', 'calendar'],
        menu_icon='cast',
        default_index=0,
        orientation='horizontal',
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "blue", "font-size": "20px"},
            "nav-link": {"font-size": "15px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#4CAF50"},
        }
    )

    def view_player_stats(data, league_avg, player_type, metrics, season=None):
        if season:
            data = data[data['Season'] == season]
            league_avg = league_avg[league_avg['Season'] == season]

        player_names = [""] + sorted(data['PlayerName'].unique())
        player = st.selectbox(get_text('select_player', lang), player_names, index=0)

        if player:
            player_data = data[data['PlayerName'] == player].sort_values(by='Season')
            player_data_styled = player_data.style.format(precision=3)

            if player_type == '투수':
                player_data_styled = player_data.style.format({
                    "EarnedRunAverage": "{:.2f}",
                    "Whip": "{:.2f}",
                    "InningsPitched": "{:.1f}"
                })

            if not player_data.empty:
                player_id = player_data.iloc[0]['PlayerID']
                profile_url = f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/{player_id}/headshot/67/current"

                col1, col2 = st.columns([1, 2])

                with col1:
                    try:
                        st.image(profile_url, caption=f"{player}의 프로필 사진", width=200)
                    except:
                        st.warning("프로필 사진을 불러올 수 없습니다.")

                with col2:
                    st.write(f"**{player}**")
                    if season:
                        st.write(f"**{season} 시즌**")

                st.dataframe(player_data_styled, height=min(400, 50 + 35 * len(player_data)))

                st.subheader("선수 기록 시각화")
                if player_type == '타자':
                    metrics_to_display = batting_metrics
                else:
                    metrics_to_display = pitching_metrics

                num_cols = 2
                rows = (len(metrics_to_display) + num_cols - 1) // num_cols
                fig, axes = plt.subplots(rows, num_cols, figsize=(15, 5 * rows))

                min_year = player_data['Season'].min() - 1
                max_year = player_data['Season'].max() + 1

                for ax, metric in zip(axes.flatten(), metrics_to_display):
                    sns.lineplot(data=player_data, x='Season', y=metric, ax=ax, marker='o', label='Player')
                    sns.lineplot(data=league_avg, x='Season', y=metric, ax=ax, marker='o', color='red', label='League Average')
                    ax.set_title(f"{player}의 시즌별 {metric} 변화", fontproperties=fontprop)
                    ax.set_xlabel('Season', fontproperties=fontprop)
                    ax.set_ylabel(metric, fontproperties=fontprop)
                    ax.set_xlim(min_year, max_year)
                    ax.legend()
                    ax.tick_params(axis='x', rotation=45)
                    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

                for ax in axes.flatten()[len(metrics_to_display):]:
                    ax.axis('off')

                plt.subplots_adjust(wspace=0.5)  # 열 사이 간격 조정
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning(f"해당 선수의 기록을 찾을 수 없습니다.")

    def view_player_stats_by_season(data, league_avg, player_type, metrics, season):
        player_names = [""] + sorted(data['PlayerName'].unique())
        player = st.selectbox('선수를 선택하세요:', player_names, index=0)

        if player and season:
            player_data = data[(data['PlayerName'] == player) & (data['Season'] == season)]
            league_data = league_avg[league_avg['Season'] == season]

            if not player_data.empty:
                player_id = player_data.iloc[0]['PlayerID']
                profile_url = f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/{player_id}/headshot/67/current"

                col1, col2 = st.columns([1, 2])

                with col1:
                    try:
                        st.image(profile_url, caption=f"{player}의 프로필 사진", width=200)
                    except:
                        st.warning("프로필 사진을 불러올 수 없습니다.")

                with col2:
                    st.write(f"**{player}**")
                    st.write(f"**{season} 시즌**")

                player_data_styled = player_data.style.format(precision=3)
                if player_type == '투수':
                    player_data_styled = player_data.style.format({
                        "EarnedRunAverage": "{:.2f}",
                        "Whip": "{:.2f}",
                        "InningsPitched": "{:.1f}"
                    })

                st.dataframe(player_data_styled, height=min(400, 50 + 35 * len(player_data)))

                st.subheader("선수와 리그 평균 비교 (히스토그램)")

                fig, ax = plt.subplots(figsize=(15, 7))
                bar_width = 0.35
                index = range(len(metrics))

                player_values = player_data[metrics].values.flatten()
                league_values = league_data[metrics].mean().values.flatten()

                bars1 = ax.bar(index, player_values, bar_width, label=player, color='b')
                bars2 = ax.bar([i + bar_width for i in index], league_values, bar_width, label='League Average', color='r')

                ax.set_xlabel('Metrics', fontproperties=fontprop)
                ax.set_ylabel('Values', fontproperties=fontprop)
                ax.set_title(f'{player} vs League Average ({season})', fontproperties=fontprop)
                ax.set_xticks([i + bar_width / 2 for i in index])
                ax.set_xticklabels(metrics, fontproperties=fontprop, rotation=45)
                ax.legend()

                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning(f"해당 시즌에 대한 선수의 기록을 찾을 수 없습니다.")

    def view_bat_stats(season=None):
        view_player_stats(df, batting_league_avg, "타자", batting_metrics, season)

    def view_pit_stats(season=None):
        view_player_stats(df_pitchers, pitching_league_avg, "투수", pitching_metrics, season)

    def view_bat_stats_by_season(season):
        view_player_stats_by_season(df, batting_league_avg, "타자", batting_metrics, season)

    def view_pit_stats_by_season(season):
        view_player_stats_by_season(df_pitchers, pitching_league_avg, "투수", pitching_metrics, season)

    if selected == '타자(선수기준)':
        view_bat_stats()
    elif selected == '타자(시즌기준)':
        season = st.selectbox("시즌을 선택하세요:", options=sorted(df['Season'].unique()))
        view_bat_stats_by_season(season)
    elif selected == '투수(선수기준)':
        view_pit_stats()
    elif selected == '투수(시즌기준)':
        season = st.selectbox("시즌을 선택하세요:", options=sorted(df_pitchers['Season'].unique()))
        view_pit_stats_by_season(season)

if __name__ == "__main__":
    run_search()
