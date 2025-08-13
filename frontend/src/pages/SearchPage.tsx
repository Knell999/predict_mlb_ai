import { useQuery } from '@tanstack/react-query'
import { playerApi } from '@/services/api'
import { usePlayerSearch } from '@/hooks/usePlayerSearch'
import PlayerCard from '@/components/player/PlayerCard'
import SearchForm from '@/components/forms/SearchForm'
import LoadingSpinner from '@/components/common/LoadingSpinner'
import ErrorMessage from '@/components/common/ErrorMessage'
import EmptyState from '@/components/common/EmptyState'
import Pagination from '@/components/common/Pagination'

export default function SearchPage() {
  const {
    searchQuery,
    searchResults,
    isLoading,
    error,
    updateQuery,
    refetch,
  } = usePlayerSearch()

  const { data: teams = [] } = useQuery({
    queryKey: ['teams'],
    queryFn: () => playerApi.getTeamList(),
  })

  const { data: seasons = [] } = useQuery({
    queryKey: ['seasons'],
    queryFn: () => playerApi.getSeasonList(),
  })

  const currentPage = Math.floor(searchQuery.offset! / searchQuery.limit!) + 1
  const totalPages = searchResults ? Math.ceil(searchResults.total / searchQuery.limit!) : 0

  const handlePageChange = (page: number) => {
    const newOffset = (page - 1) * searchQuery.limit!
    updateQuery({ offset: newOffset })
  }

  return (
    <div className="space-y-6">
      {/* 페이지 헤더 */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">선수 검색</h1>
        <p className="text-gray-600 mt-2">
          MLB 선수들의 기록을 검색하고 상세 정보를 확인하세요.
        </p>
      </div>

      {/* 검색 폼 */}
      <SearchForm
        searchQuery={searchQuery}
        onQueryChange={updateQuery}
        teams={teams}
        seasons={seasons}
      />

      {/* 검색 결과 */}
      {isLoading && (
        <div className="flex justify-center py-12">
          <LoadingSpinner />
        </div>
      )}

      {error && (
        <ErrorMessage
          message={`검색 중 오류가 발생했습니다: ${error.message}`}
          onRetry={() => refetch()}
        />
      )}

      {searchResults && (
        <div>
          {/* 결과 헤더 */}
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              검색 결과 ({searchResults.total.toLocaleString()}건)
            </h2>
          </div>

          {/* 결과 목록 */}
          {searchResults.results.length === 0 ? (
            <EmptyState
              title="검색 결과가 없습니다"
              description="검색 조건에 맞는 선수를 찾을 수 없습니다. 다른 검색어나 필터를 시도해보세요."
            />
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                {searchResults.results.map((player, index) => (
                  <PlayerCard 
                    key={`${player.player_name}-${player.season}-${index}`} 
                    player={player} 
                  />
                ))}
              </div>

              {/* 페이지네이션 */}
              {totalPages > 1 && (
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={handlePageChange}
                  showInfo={true}
                  totalItems={searchResults.total}
                  itemsPerPage={searchQuery.limit!}
                />
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}