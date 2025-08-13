import { BatterStats, PitcherStats, ChartData } from '@/types'

// 타자 통계를 차트 데이터로 변환
export function batterStatsToChartData(
  stats: BatterStats[], 
  statKeys: (keyof BatterStats)[],
  labels?: string[]
): ChartData {
  const actualLabels = labels || stats.map(s => s.season.toString())
  
  const datasets = statKeys.map((key, index) => {
    const colors = [
      'rgb(59, 130, 246)', // blue
      'rgb(34, 197, 94)',  // green
      'rgb(239, 68, 68)',  // red
      'rgb(168, 85, 247)', // purple
      'rgb(245, 158, 11)', // amber
    ]
    
    return {
      label: getStatLabel(key as string),
      data: stats.map(s => s[key] as number || 0),
      backgroundColor: colors[index % colors.length] + '20',
      borderColor: colors[index % colors.length],
      borderWidth: 2,
      fill: false,
    }
  })
  
  return {
    labels: actualLabels,
    datasets,
  }
}

// 투수 통계를 차트 데이터로 변환
export function pitcherStatsToChartData(
  stats: PitcherStats[], 
  statKeys: (keyof PitcherStats)[],
  labels?: string[]
): ChartData {
  const actualLabels = labels || stats.map(s => s.season.toString())
  
  const datasets = statKeys.map((key, index) => {
    const colors = [
      'rgb(59, 130, 246)', // blue
      'rgb(34, 197, 94)',  // green
      'rgb(239, 68, 68)',  // red
      'rgb(168, 85, 247)', // purple
      'rgb(245, 158, 11)', // amber
    ]
    
    return {
      label: getStatLabel(key as string),
      data: stats.map(s => s[key] as number || 0),
      backgroundColor: colors[index % colors.length] + '20',
      borderColor: colors[index % colors.length],
      borderWidth: 2,
      fill: false,
    }
  })
  
  return {
    labels: actualLabels,
    datasets,
  }
}

// 통계 키를 사용자 친화적 라벨로 변환
export function getStatLabel(key: string): string {
  const labels: Record<string, string> = {
    // 타자 통계
    batting_average: '타율',
    on_base_percentage: '출루율',
    slugging_percentage: '장타율',
    ops: 'OPS',
    hits: '안타',
    home_runs: '홈런',
    rbi: '타점',
    runs: '득점',
    stolen_bases: '도루',
    strikeouts: '삼진',
    walks: '볼넷',
    games: '경기수',
    at_bats: '타수',
    doubles: '2루타',
    triples: '3루타',
    
    // 투수 통계
    era: '평균자책점',
    whip: 'WHIP',
    wins: '승',
    losses: '패',
    saves: '세이브',
    innings_pitched: '이닝',
    hits_allowed: '피안타',
    earned_runs: '자책점',
    home_runs_allowed: '피홈런',
    games_started: '선발',
    complete_games: '완투',
    shutouts: '완봉',
  }
  
  return labels[key] || key
}

// 색상 팔레트 생성
export function generateColors(count: number): string[] {
  const baseColors = [
    'rgb(59, 130, 246)',  // blue
    'rgb(34, 197, 94)',   // green
    'rgb(239, 68, 68)',   // red
    'rgb(168, 85, 247)',  // purple
    'rgb(245, 158, 11)',  // amber
    'rgb(236, 72, 153)',  // pink
    'rgb(20, 184, 166)',  // teal
    'rgb(251, 146, 60)',  // orange
  ]
  
  const colors: string[] = []
  for (let i = 0; i < count; i++) {
    colors.push(baseColors[i % baseColors.length])
  }
  
  return colors
}

// 차트 옵션 생성 헬퍼
export function createChartOptions(
  title?: string,
  xAxisTitle?: string,
  yAxisTitle?: string
) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: !!title,
        text: title,
      },
    },
    scales: {
      x: {
        display: true,
        title: {
          display: !!xAxisTitle,
          text: xAxisTitle,
        },
      },
      y: {
        display: true,
        title: {
          display: !!yAxisTitle,
          text: yAxisTitle,
        },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
  }
}

// 통계값 포맷팅
export function formatStat(value: number | undefined, statKey: string): string {
  if (value === undefined || value === null) return '-'
  
  // 소수점 3자리 통계 (타율, 출루율 등)
  const threeDecimalStats = [
    'batting_average', 'on_base_percentage', 'slugging_percentage', 'ops'
  ]
  
  // 소수점 2자리 통계 (ERA, WHIP 등)
  const twoDecimalStats = [
    'era', 'whip'
  ]
  
  if (threeDecimalStats.includes(statKey)) {
    return value.toFixed(3)
  } else if (twoDecimalStats.includes(statKey)) {
    return value.toFixed(2)
  } else {
    return Math.round(value).toString()
  }
}