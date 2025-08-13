import { useQuery } from '@tanstack/react-query'
import { playerApi } from '@/services/api'

export default function HealthCheck() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['health-check'],
    queryFn: playerApi.getStatsSummary,
    retry: 3,
  })

  if (isLoading) {
    return (
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
        <div className="flex">
          <div className="ml-3">
            <p className="text-sm text-yellow-700">
              🔄 백엔드 서버 연결 확인 중...
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
        <div className="flex">
          <div className="ml-3">
            <p className="text-sm text-red-700">
              ❌ 백엔드 서버 연결 실패: {error.message}
            </p>
            <p className="text-xs text-red-600 mt-1">
              백엔드 서버(http://localhost:8001)가 실행 중인지 확인하세요.
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (data) {
    return (
      <div className="bg-green-50 border-l-4 border-green-400 p-4 mb-4">
        <div className="flex">
          <div className="ml-3">
            <p className="text-sm text-green-700">
              ✅ 백엔드 연결 성공 - 총 {data.total_players.toLocaleString()}명의 선수 데이터 로드됨
            </p>
          </div>
        </div>
      </div>
    )
  }

  return null
}