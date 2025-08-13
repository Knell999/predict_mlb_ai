import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { playerApi } from '@/services/api'
import { PlayerSearchQuery } from '@/types'

export function usePlayerSearch(initialQuery: PlayerSearchQuery = {}) {
  const [searchQuery, setSearchQuery] = useState<PlayerSearchQuery>({
    limit: 20,
    offset: 0,
    ...initialQuery,
  })

  const {
    data: searchResults,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['player-search', searchQuery],
    queryFn: () => playerApi.searchPlayers(searchQuery),
    enabled: !!(
      searchQuery.query || 
      searchQuery.player_type || 
      searchQuery.team || 
      searchQuery.season
    ),
  })

  const updateQuery = (updates: Partial<PlayerSearchQuery>) => {
    setSearchQuery(prev => ({
      ...prev,
      ...updates,
      offset: updates.offset ?? 0, // 새로운 필터 시 첫 페이지로 리셋
    }))
  }

  const resetQuery = () => {
    setSearchQuery({
      limit: 20,
      offset: 0,
    })
  }

  const nextPage = () => {
    if (searchResults && searchQuery.offset! + searchQuery.limit! < searchResults.total) {
      updateQuery({ offset: searchQuery.offset! + searchQuery.limit! })
    }
  }

  const prevPage = () => {
    if (searchQuery.offset! > 0) {
      updateQuery({ offset: Math.max(0, searchQuery.offset! - searchQuery.limit!) })
    }
  }

  const hasNextPage = searchResults ? searchQuery.offset! + searchQuery.limit! < searchResults.total : false
  const hasPrevPage = searchQuery.offset! > 0

  return {
    searchQuery,
    searchResults,
    isLoading,
    error,
    updateQuery,
    resetQuery,
    refetch,
    nextPage,
    prevPage,
    hasNextPage,
    hasPrevPage,
  }
}