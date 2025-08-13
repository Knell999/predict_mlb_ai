import axios from 'axios'
import { 
  PlayerSearchQuery, 
  PlayerSearchResponse, 
  StatsSummary, 
  PlayerType,
  APIResponse,
  AnalysisRequest,
  AnalysisResponse
} from '@/types'

// API 클라이언트 생성
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 응답 인터셉터
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// API 함수들
export const playerApi = {
  // 통계 요약 조회
  getStatsSummary: async (): Promise<StatsSummary> => {
    const response = await api.get<StatsSummary>('/players/summary')
    return response.data
  },

  // 선수 검색
  searchPlayers: async (query: PlayerSearchQuery): Promise<PlayerSearchResponse> => {
    const params = new URLSearchParams()
    
    if (query.query) params.append('query', query.query)
    if (query.player_type) params.append('player_type', query.player_type)
    if (query.team) params.append('team', query.team)
    if (query.season) params.append('season', query.season.toString())
    if (query.limit) params.append('limit', query.limit.toString())
    if (query.offset) params.append('offset', query.offset.toString())
    
    const response = await api.get<PlayerSearchResponse>(`/players/search?${params}`)
    return response.data
  },

  // 선수 상세 통계 조회
  getPlayerStats: async (
    playerId: string,
    playerType: PlayerType,
    seasonStart?: number,
    seasonEnd?: number
  ) => {
    const params = new URLSearchParams()
    params.append('player_type', playerType)
    if (seasonStart) params.append('season_start', seasonStart.toString())
    if (seasonEnd) params.append('season_end', seasonEnd.toString())
    
    const response = await api.get<APIResponse>(`/players/${playerId}/stats?${params}`)
    return response.data
  },

  // 타자 목록 조회
  getBatterList: async (season?: number, team?: string, limit?: number): Promise<string[]> => {
    const params = new URLSearchParams()
    if (season) params.append('season', season.toString())
    if (team) params.append('team', team)
    if (limit) params.append('limit', limit.toString())
    
    const response = await api.get<string[]>(`/players/batters?${params}`)
    return response.data
  },

  // 투수 목록 조회
  getPitcherList: async (season?: number, team?: string, limit?: number): Promise<string[]> => {
    const params = new URLSearchParams()
    if (season) params.append('season', season.toString())
    if (team) params.append('team', team)
    if (limit) params.append('limit', limit.toString())
    
    const response = await api.get<string[]>(`/players/pitchers?${params}`)
    return response.data
  },

  // 팀 목록 조회
  getTeamList: async (playerType?: PlayerType, season?: number): Promise<string[]> => {
    const params = new URLSearchParams()
    if (playerType) params.append('player_type', playerType)
    if (season) params.append('season', season.toString())
    
    const response = await api.get<string[]>(`/players/teams?${params}`)
    return response.data
  },

  // 시즌 목록 조회
  getSeasonList: async (playerType?: PlayerType): Promise<number[]> => {
    const params = new URLSearchParams()
    if (playerType) params.append('player_type', playerType)
    
    const response = await api.get<number[]>(`/players/seasons?${params}`)
    return response.data
  },
}

// AI 분석 API (향후 구현)
export const analysisApi = {
  // AI 분석 요청
  requestAnalysis: async (request: AnalysisRequest): Promise<AnalysisResponse> => {
    const response = await api.post<AnalysisResponse>('/analysis', request)
    return response.data
  },

  // 분석 결과 조회
  getAnalysis: async (analysisId: string): Promise<AnalysisResponse> => {
    const response = await api.get<AnalysisResponse>(`/analysis/${analysisId}`)
    return response.data
  },
}

export default api