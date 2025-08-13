import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  Search, 
  GitCompare, 
  Brain, 
  TrendingUp,
  Users
} from 'lucide-react'
import clsx from 'clsx'

const navigation = [
  { name: '홈', href: '/', icon: Home },
  { name: '선수 검색', href: '/search', icon: Search },
  { name: '선수 비교', href: '/compare', icon: GitCompare },
  { name: 'AI 분석', href: '/analysis', icon: Brain },
]

const stats = [
  { name: '통계 트렌드', href: '/stats', icon: TrendingUp },
  { name: '팀 분석', href: '/teams', icon: Users },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <div className="w-64 bg-white shadow-sm border-r border-gray-200">
      <div className="p-6">
        {/* 주요 메뉴 */}
        <nav className="space-y-1">
          <div className="mb-4">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              주요 기능
            </h3>
          </div>
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={clsx(
                  isActive
                    ? 'bg-primary-50 border-primary-500 text-primary-700'
                    : 'border-transparent text-gray-600 hover:bg-gray-50 hover:text-gray-900',
                  'group flex items-center pl-3 pr-4 py-2 border-l-4 text-sm font-medium transition-colors'
                )}
              >
                <item.icon
                  className={clsx(
                    isActive ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500',
                    'mr-3 flex-shrink-0 h-5 w-5'
                  )}
                />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* 통계 메뉴 */}
        <nav className="mt-8 space-y-1">
          <div className="mb-4">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              통계 분석
            </h3>
          </div>
          {stats.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={clsx(
                  isActive
                    ? 'bg-primary-50 border-primary-500 text-primary-700'
                    : 'border-transparent text-gray-600 hover:bg-gray-50 hover:text-gray-900',
                  'group flex items-center pl-3 pr-4 py-2 border-l-4 text-sm font-medium transition-colors'
                )}
              >
                <item.icon
                  className={clsx(
                    isActive ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500',
                    'mr-3 flex-shrink-0 h-5 w-5'
                  )}
                />
                {item.name}
              </Link>
            )
          })}
        </nav>
      </div>
    </div>
  )
}