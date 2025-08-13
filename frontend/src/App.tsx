import { Routes, Route } from 'react-router-dom'
import Layout from '@/components/layout/Layout'
import HomePage from '@/pages/HomePage'
import SearchPage from '@/pages/SearchPage'
import PlayerDetailPage from '@/pages/PlayerDetailPage'
import ComparePage from '@/pages/ComparePage'
import AnalysisPage from '@/pages/AnalysisPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/player/:playerId" element={<PlayerDetailPage />} />
        <Route path="/compare" element={<ComparePage />} />
        <Route path="/analysis" element={<AnalysisPage />} />
      </Routes>
    </Layout>
  )
}

export default App