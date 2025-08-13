// API 응답 기본 타입
export interface APIResponse<T = any> {
  success: boolean
  message: string
  data?: T
}

// 선수 타입
export enum PlayerType {
  BATTER = 'batter',
  PITCHER = 'pitcher'
}

// 타자 통계
export interface BatterStats {
  season: number
  batting_average?: number
  on_base_percentage?: number
  slugging_percentage?: number
  ops?: number
  hits?: number
  home_runs?: number
  rbi?: number
  runs?: number
  stolen_bases?: number
  strikeouts?: number
  walks?: number
  games?: number
  at_bats?: number
  doubles?: number
  triples?: number
}

// 투수 통계
export interface PitcherStats {
  season: number
  era?: number
  whip?: number
  wins?: number
  losses?: number
  saves?: number
  strikeouts?: number
  walks?: number
  innings_pitched?: number
  hits_allowed?: number
  earned_runs?: number
  home_runs_allowed?: number
  games?: number
  games_started?: number
  complete_games?: number
  shutouts?: number
}

// 선수 기본 정보
export interface PlayerRecord {
  player_name: string
  team: string
  season: number
  player_type: PlayerType
  stats: BatterStats | PitcherStats
}

// 타자 기록
export interface BatterRecord extends PlayerRecord {
  player_type: PlayerType.BATTER
  stats: BatterStats
}

// 투수 기록
export interface PitcherRecord extends PlayerRecord {
  player_type: PlayerType.PITCHER
  stats: PitcherStats
}

// 검색 쿼리
export interface PlayerSearchQuery {
  query?: string
  player_type?: PlayerType
  team?: string
  season?: number
  limit?: number
  offset?: number
}

// 검색 결과
export interface PlayerSearchResponse {
  results: PlayerRecord[]
  total: number
  offset: number
  limit: number
}

// 통계 요약
export interface StatsSummary {
  total_players: number
  batter_count: number
  pitcher_count: number
  total_seasons: number
  latest_season: number
  earliest_season: number
  last_updated?: string
}

// 차트 데이터 타입
export interface ChartDataPoint {
  x: number | string
  y: number
  label?: string
}

export interface ChartData {
  labels: string[]
  datasets: Array<{
    label: string
    data: number[]
    backgroundColor?: string | string[]
    borderColor?: string | string[]
    borderWidth?: number
    fill?: boolean
  }>
}

// AI 분석 관련 타입
export interface AnalysisRequest {
  player_name: string
  player_type: PlayerType
  language?: 'korean' | 'english' | 'japanese'
  analysis_type?: 'individual' | 'comparison'
  comparison_player?: string
}

export interface AnalysisResponse {
  player_name: string
  analysis_text: string
  generated_at: string
  analysis_type: string
  language: string
}