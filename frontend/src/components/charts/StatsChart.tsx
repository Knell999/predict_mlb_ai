import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
} from 'chart.js'
import { Line, Bar } from 'react-chartjs-2'
import { ChartData } from '@/types'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface StatsChartProps {
  data: ChartData
  type?: 'line' | 'bar'
  title?: string
  height?: number
  options?: any
}

export default function StatsChart({ 
  data, 
  type = 'line', 
  title, 
  height = 300,
  options: customOptions
}: StatsChartProps) {
  const defaultOptions = {
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
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
        },
      },
      y: {
        display: true,
        title: {
          display: true,
        },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
  }

  const mergedOptions = {
    ...defaultOptions,
    ...customOptions,
  }

  return (
    <div className="card">
      <div style={{ height }}>
        {type === 'line' ? (
          <Line data={data} options={mergedOptions} />
        ) : (
          <Bar data={data} options={mergedOptions} />
        )}
      </div>
    </div>
  )
}