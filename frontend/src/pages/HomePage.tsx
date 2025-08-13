import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Search, GitCompare, Brain, TrendingUp } from 'lucide-react'
import { playerApi } from '@/services/api'
import HealthCheck from '@/components/common/HealthCheck'

export default function HomePage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats-summary'],
    queryFn: playerApi.getStatsSummary,
  })

  const features = [
    {
      name: '선수 검색',
      description: 'MLB 선수들의 상세한 기록과 통계를 검색하고 조회할 수 있습니다.',
      icon: Search,
      href: '/search',
      color: 'text-blue-600 bg-blue-100',
    },
    {
      name: '선수 비교',
      description: '두 선수의 성능을 직접 비교하여 차이점을 분석할 수 있습니다.',
      icon: GitCompare,
      href: '/compare',
      color: 'text-green-600 bg-green-100',
    },
    {
      name: 'AI 분석',
      description: 'AI 기반 분석으로 선수의 경기력과 트렌드를 심층 분석합니다.',
      icon: Brain,
      href: '/analysis',
      color: 'text-purple-600 bg-purple-100',
    },
    {
      name: '통계 트렌드',
      description: '시즌별, 팀별 통계 트렌드를 시각화하여 확인할 수 있습니다.',
      icon: TrendingUp,
      href: '/stats',
      color: 'text-orange-600 bg-orange-100',
    },
  ]

  return (
    <div className="space-y-8">
      {/* 연결 상태 체크 */}
      <HealthCheck />
      
      {/* 헤로 섹션 */}
      <div className="text-center py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          MLB 선수 분석 시스템
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          2000년부터 2023년까지의 MLB 선수 데이터를 기반으로 
          상세한 통계 분석과 AI 기반 인사이트를 제공합니다.
        </p>
      </div>

      {/* 통계 카드 */}
      {!isLoading && stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="card text-center">
            <div className="text-3xl font-bold text-primary-600 mb-2">
              {stats.total_players.toLocaleString()}
            </div>
            <div className="text-gray-600">총 선수 수</div>
          </div>
          <div className="card text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {stats.batter_count.toLocaleString()}
            </div>
            <div className="text-gray-600">타자</div>
          </div>
          <div className="card text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {stats.pitcher_count.toLocaleString()}
            </div>
            <div className="text-gray-600">투수</div>
          </div>
          <div className="card text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {stats.total_seasons}
            </div>
            <div className="text-gray-600">시즌</div>
          </div>
        </div>
      )}

      {/* 기능 소개 */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          주요 기능
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature) => (
            <Link
              key={feature.name}
              to={feature.href}
              className="card hover:shadow-md transition-shadow group cursor-pointer"
            >
              <div className="flex items-start space-x-4">
                <div className={`p-3 rounded-lg ${feature.color}`}>
                  <feature.icon className="h-6 w-6" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                    {feature.name}
                  </h3>
                  <p className="text-gray-600 mt-1">
                    {feature.description}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* 빠른 시작 */}
      <div className="card bg-primary-50 border-primary-200">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-primary-900 mb-4">
            지금 시작하세요
          </h2>
          <p className="text-primary-700 mb-6">
            원하는 선수를 검색하여 상세한 통계와 AI 분석을 확인해보세요.
          </p>
          <Link
            to="/search"
            className="btn-primary inline-flex items-center space-x-2"
          >
            <Search className="h-4 w-4" />
            <span>선수 검색하기</span>
          </Link>
        </div>
      </div>
    </div>
  )
}