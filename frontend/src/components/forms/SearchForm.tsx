import { Search, User, Users, Calendar, Filter } from 'lucide-react'
import { PlayerSearchQuery, PlayerType } from '@/types'

interface SearchFormProps {
  searchQuery: PlayerSearchQuery
  onQueryChange: (updates: Partial<PlayerSearchQuery>) => void
  teams?: string[]
  seasons?: number[]
  onSubmit?: (e: React.FormEvent) => void
}

export default function SearchForm({ 
  searchQuery, 
  onQueryChange, 
  teams = [], 
  seasons = [],
  onSubmit 
}: SearchFormProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit?.(e)
  }

  return (
    <div className="card">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 검색어 입력 */}
        <div>
          <label className="label">선수 이름</label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              className="input pl-10"
              placeholder="선수 이름을 입력하세요..."
              value={searchQuery.query || ''}
              onChange={(e) => onQueryChange({ query: e.target.value })}
            />
          </div>
        </div>

        {/* 필터 옵션 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* 선수 타입 */}
          <div>
            <label className="label">선수 타입</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <select
                className="input pl-10"
                value={searchQuery.player_type || ''}
                onChange={(e) => onQueryChange({ player_type: e.target.value as PlayerType || undefined })}
              >
                <option value="">전체</option>
                <option value={PlayerType.BATTER}>타자</option>
                <option value={PlayerType.PITCHER}>투수</option>
              </select>
            </div>
          </div>

          {/* 팀 선택 */}
          <div>
            <label className="label">팀</label>
            <div className="relative">
              <Users className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <select
                className="input pl-10"
                value={searchQuery.team || ''}
                onChange={(e) => onQueryChange({ team: e.target.value || undefined })}
              >
                <option value="">전체 팀</option>
                {teams.map((team) => (
                  <option key={team} value={team}>
                    {team}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* 시즌 선택 */}
          <div>
            <label className="label">시즌</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <select
                className="input pl-10"
                value={searchQuery.season || ''}
                onChange={(e) => onQueryChange({ season: e.target.value ? parseInt(e.target.value) : undefined })}
              >
                <option value="">전체 시즌</option>
                {seasons.map((season) => (
                  <option key={season} value={season}>
                    {season}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* 결과 수 제한 */}
          <div>
            <label className="label">결과 수</label>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <select
                className="input pl-10"
                value={searchQuery.limit || 20}
                onChange={(e) => onQueryChange({ limit: parseInt(e.target.value) })}
              >
                <option value={10}>10개</option>
                <option value={20}>20개</option>
                <option value={50}>50개</option>
                <option value={100}>100개</option>
              </select>
            </div>
          </div>
        </div>

        <div className="flex gap-2">
          <button type="submit" className="btn-primary">
            <Search className="h-4 w-4 mr-2" />
            검색
          </button>
          <button 
            type="button" 
            className="btn-secondary"
            onClick={() => onQueryChange({ 
              query: '', 
              player_type: undefined, 
              team: undefined, 
              season: undefined 
            })}
          >
            초기화
          </button>
        </div>
      </form>
    </div>
  )
}