"""
다국어 지원을 위한 다국어 사전 모듈입니다.
"""

# 한국어 텍스트 사전
KO = {
    # 공통
    "app_title": "MLB 선수 기록 조회 및 예측 서비스",
    "home": "홈",
    "trend_analysis": "트렌드 분석",
    "search_records": "기록 조회",
    "predict_records": "기록 예측",
    "compare_players": "선수 비교",

    # 선수 비교 페이지
    "select_data_type": "데이터 종류 선택",
    "batter": "타자",
    "pitcher": "투수",
    "select_player_1": "첫 번째 선수 선택",
    "select_player_2": "두 번째 선수 선택",
    "select_stats_to_compare": "비교할 스탯 선택",
    "select_stats_prompt": "비교할 스탯을 하나 이상 선택하세요.",
    "select_different_players": "서로 다른 두 명의 선수를 선택하세요.",
    "career_summary": "커리어 통산 비교",
    "season_by_season": "시즌별 스탯 비교",
    "no_data_available": "표시할 데이터가 없습니다.",
    
    # 홈 페이지
    "welcome_message": "야구 팬 여러분, 안녕하세요! 👋",
    "app_intro": "MLB 선수 기록 조회 및 예측 서비스에 오신 것을 환영합니다. 🎉",
    "app_description": "이 플랫폼은 **Major League Baseball (MLB)** 선수들의 기록을 쉽게 조회하고, 다양한 지표를 분석하며, 앞으로의 성과를 예측할 수 있는 종합적인 대시보드입니다. 📈",
    "main_features": "✨ 주요 기능 ✨",
    "search_feature": "🔍 선수 기록 조회",
    "prediction_feature": "🔮 성과 예측",
    "visualization_feature": "📈 데이터 시각화",
    "learn_more": "🤔 더 알아보기",
    
    # 검색 페이지
    "search_title": "MLB 선수 기록 조회👁️",
    "select_player": "선수를 선택하세요:",
    "select_season": "시즌을 선택하세요:",
    "player_info": "선수 정보",
    "visualization_title": "선수 기록 시각화",
    "compare_with_league": "선수와 리그 평균 비교 (히스토그램)",
    "no_record": "해당 선수의 기록을 찾을 수 없습니다.",
    
    # 예측 페이지
    "predict_title": "MLB 선수 기록 예측",
    "player_option": "선수 및 옵션 선택",
    "prediction_tab": "기록 예측",
    "prediction_result": "예측 결과",
    "prediction_warning": "의 최근 2개년(2022, 2023) 시즌 데이터가 없어 예측이 불가능합니다.",
    
    # 트렌드 페이지
    "trend_title": "MLB 리그 트렌드 분석",
    "select_metrics": "분석할 지표 선택",
    "trend_overview": "리그 평균 지표 변화 추이",
    "moving_average": "이동평균 설명",
    "select_metric_warning": "분석할 지표를 하나 이상 선택해주세요.",
    
    # 데이터 상태 페이지
    "data_status": "데이터 상태",
    "data_status_title": "데이터 상태 모니터링",
    
    # 기타
    "loading": "로딩 중...",
    "error": "오류가 발생했습니다",
    "year": "년",
    "player": "선수",
    "team": "팀",
    "stats": "기록",
}

# 영어 텍스트 사전
EN = {
    # Common
    "app_title": "MLB Player Stats Search and Prediction Service",
    "home": "Home",
    "trend_analysis": "Trend Analysis",
    "search_records": "Search Records",
    "predict_records": "Predict Records",
    "compare_players": "Compare Players",

    # Compare Players Page
    "select_data_type": "Select Data Type",
    "batter": "Batter",
    "pitcher": "Pitcher",
    "select_player_1": "Select Player 1",
    "select_player_2": "Select Player 2",
    "select_stats_to_compare": "Select Stats to Compare",
    "select_stats_prompt": "Please select at least one stat to compare.",
    "select_different_players": "Please select two different players.",
    "career_summary": "Career Summary Comparison",
    "season_by_season": "Season-by-Season Stat Comparison",
    "no_data_available": "No data available to display.",
    
    # Home page
    "welcome_message": "Hello, baseball fans! 👋",
    "app_intro": "Welcome to the MLB Player Stats Search and Prediction Service! 🎉",
    "app_description": "This platform is a comprehensive dashboard that allows you to easily search for **Major League Baseball (MLB)** player records, analyze various metrics, and predict future performance. 📈",
    "main_features": "✨ Main Features ✨",
    "search_feature": "🔍 Player Records Search",
    "prediction_feature": "🔮 Performance Prediction",
    "visualization_feature": "📈 Data Visualization",
    "learn_more": "🤔 Learn More",
    
    # Search page
    "search_title": "MLB Player Records Search👁️",
    "select_player": "Select a player:",
    "select_season": "Select a season:",
    "player_info": "Player Information",
    "visualization_title": "Player Records Visualization",
    "compare_with_league": "Player vs League Average (Histogram)",
    "no_record": "No records found for this player.",
    
    # Predict page
    "predict_title": "MLB Player Records Prediction",
    "player_option": "Select Player and Options",
    "prediction_tab": "Records Prediction",
    "prediction_result": "Prediction Results",
    "prediction_warning": " does not have recent data (2022, 2023) required for prediction.",
    
    # Trend page
    "trend_title": "MLB League Trend Analysis",
    "select_metrics": "Select metrics to analyze",
    "trend_overview": "League Average Metrics Trend",
    "moving_average": "Moving Average Explanation",
    "select_metric_warning": "Please select at least one metric to analyze.",
    
    # Data Status Page
    "data_status": "Data Status",
    "data_status_title": "Data Status Monitoring",
    
    # Other
    "loading": "Loading...",
    "error": "An error occurred",
    "year": "Year",
    "player": "Player",
    "team": "Team",
    "stats": "Stats",
}

# 일본어 텍스트 사전
JA = {
    # 共通
    "app_title": "MLB選手記録検索・予測サービス",
    "home": "ホーム",
    "trend_analysis": "トレンド分析",
    "search_records": "記録検索",
    "predict_records": "記録予測",
    "compare_players": "選手比較",

    # 選手比較ページ
    "select_data_type": "データタイプ選択",
    "batter": "打者",
    "pitcher": "投手",
    "select_player_1": "選手1を選択",
    "select_player_2": "選手2を選択",
    "select_stats_to_compare": "比較するステータスを選択",
    "select_stats_prompt": "比較するステータスを1つ以上選択してください。",
    "select_different_players": "異なる2人の選手を選択してください。",
    "career_summary": "キャリア通算比較",
    "season_by_season": "シーズン別ステータス比較",
    "no_data_available": "表示するデータがありません。",
    
    # ホームページ
    "welcome_message": "こんにちは、野球ファンの皆さん！ 👋",
    "app_intro": "MLB選手記録検索・予測サービスへようこそ！ 🎉",
    "app_description": "このプラットフォームは、**メジャーリーグベースボール（MLB）**選手の記録を簡単に検索し、様々な指標を分析し、将来のパフォーマンスを予測できる総合的なダッシュボードです。 📈",
    "main_features": "✨ 主な機能 ✨",
    "search_feature": "🔍 選手記録検索",
    "prediction_feature": "🔮 パフォーマンス予測",
    "visualization_feature": "📈 データ可視化",
    "learn_more": "🤔 詳細を見る",
    
    # 検索ページ
    "search_title": "MLB選手記録検索👁️",
    "select_player": "選手を選択してください:",
    "select_season": "シーズンを選択してください:",
    "player_info": "選手情報",
    "visualization_title": "選手記録の可視化",
    "compare_with_league": "選手とリーグ平均の比較（ヒストグラム）",
    "no_record": "この選手の記録が見つかりません。",
    
    # 予測ページ
    "predict_title": "MLB選手記録予測",
    "player_option": "選手とオプションの選択",
    "prediction_tab": "記録予測",
    "prediction_result": "予測結果",
    "prediction_warning": "は予測に必要な最近のデータ（2022年、2023年）がありません。",
    
    # トレンドページ
    "trend_title": "MLBリーグトレンド分析",
    "select_metrics": "分析する指標を選択",
    "trend_overview": "リーグ平均指標の変化傾向",
    "moving_average": "移動平均の説明",
    "select_metric_warning": "分析するには少なくとも1つの指標を選択してください。",
    
    # データ状態ページ
    "data_status": "データ状態",
    "data_status_title": "データ状態モニタリング",
    
    # その他
    "loading": "読み込み中...",
    "error": "エラーが発生しました",
    "year": "年",
    "player": "選手",
    "team": "チーム",
    "stats": "成績",
}

# 사용 가능한 모든 언어
LANGUAGES = {
    "ko": {"name": "한국어", "data": KO},
    "en": {"name": "English", "data": EN},
    "ja": {"name": "日本語", "data": JA}
}

def get_text(key, lang="ko"):
    """
    지정한 언어와 키로 텍스트를 가져옵니다.
    
    Args:
        key: 텍스트 키
        lang: 언어 코드 (기본값: 'ko')
    
    Returns:
        str: 해당 언어의 텍스트, 없으면 키 그대로 반환
    """
    if lang not in LANGUAGES:
        lang = "ko"  # 기본 언어
    
    return LANGUAGES[lang]["data"].get(key, key)

def get_languages():
    """
    사용 가능한 모든 언어를 반환합니다.
    
    Returns:
        dict: 언어 코드와 이름의 사전
    """
    return {code: info["name"] for code, info in LANGUAGES.items()}
