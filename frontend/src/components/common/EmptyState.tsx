import { ReactNode } from 'react'
import { Search } from 'lucide-react'

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description: string
  action?: ReactNode
}

export default function EmptyState({ 
  icon = <Search className="h-12 w-12 text-gray-400" />, 
  title, 
  description, 
  action 
}: EmptyStateProps) {
  return (
    <div className="card text-center py-12">
      <div className="flex justify-center mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 mb-6 max-w-md mx-auto">{description}</p>
      {action && <div>{action}</div>}
    </div>
  )
}