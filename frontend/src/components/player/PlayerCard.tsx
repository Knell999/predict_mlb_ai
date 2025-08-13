import { Link } from 'react-router-dom'
import { User, Calendar, Users, TrendingUp } from 'lucide-react'
import { PlayerRecord, PlayerType, BatterStats, PitcherStats } from '@/types'

interface PlayerCardProps {
  player: PlayerRecord
}

export default function PlayerCard({ player }: PlayerCardProps) {
  const isBatter = player.player_type === PlayerType.BATTER
  const stats = player.stats as BatterStats | PitcherStats

  // 타자 주요 스탯
  const getBatterMainStats = (stats: BatterStats) => [
    { label: 'AVG', value: stats.batting_average?.toFixed(3) || '-.---', icon: TrendingUp },
    { label: 'HR', value: stats.home_runs?.toString() || '0', icon: TrendingUp },
    { label: 'RBI', value: stats.rbi?.toString() || '0', icon: TrendingUp },
    { label: 'OPS', value: stats.ops?.toFixed(3) || '-.---', icon: TrendingUp },
  ]

  // 투수 주요 스탯
  const getPitcherMainStats = (stats: PitcherStats) => [
    { label: 'ERA', value: stats.era?.toFixed(2) || '-.--', icon: TrendingUp },
    { label: 'W-L', value: `${stats.wins || 0}-${stats.losses || 0}`, icon: TrendingUp },
    { label: 'SO', value: stats.strikeouts?.toString() || '0', icon: TrendingUp },
    { label: 'WHIP', value: stats.whip?.toFixed(2) || '-.--', icon: TrendingUp },
  ]

  const mainStats = isBatter ? getBatterMainStats(stats as BatterStats) : getPitcherMainStats(stats as PitcherStats)

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-100 rounded-full">
            <User className="h-5 w-5 text-primary-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{player.player_name}</h3>
            <div className="flex items-center space-x-2 text-sm text-gray-500 mt-1">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                isBatter ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
              }`}>
                {isBatter ? '타자' : '투수'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 팀과 시즌 정보 */}
      <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
        <div className="flex items-center space-x-1">
          <Users className="h-4 w-4" />
          <span>{player.team}</span>
        </div>
        <div className="flex items-center space-x-1">
          <Calendar className="h-4 w-4" />
          <span>{player.season}</span>
        </div>
      </div>

      {/* 주요 통계 */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {mainStats.map((stat, index) => (
          <div key={index} className="text-center p-2 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-500 mb-1">{stat.label}</div>
            <div className="font-semibold text-gray-900">{stat.value}</div>
          </div>
        ))}
      </div>

      {/* 액션 버튼 */}
      <div className="flex space-x-2">
        <Link
          to={`/player/${encodeURIComponent(player.player_name)}?type=${player.player_type}&season=${player.season}&team=${player.team}`}
          className="btn-primary flex-1 text-center text-sm py-2"
        >
          상세 보기
        </Link>
        <button className="btn-secondary text-sm py-2 px-3">
          비교 추가
        </button>
      </div>
    </div>
  )
}