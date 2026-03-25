import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Moon, Sun, ArrowLeft } from 'lucide-react'
import { useSession } from '../store/sessionStore'
import { getSession } from '../api/client'
import { Sidebar } from '../components/layout/Sidebar'
import { TabNav } from '../components/layout/TabNav'
import { DataOverview } from '../components/tabs/DataOverview'
import { MissingValues } from '../components/tabs/MissingValues'
import { Distributions } from '../components/tabs/Distributions'
import { Correlations } from '../components/tabs/Correlations'
import { Categories } from '../components/tabs/Categories'
import { TimeSeries } from '../components/tabs/TimeSeries'
import { Preprocessing } from '../components/tabs/Preprocessing'
import { AIInsights } from '../components/tabs/AIInsights'
import { QualityBadge } from '../components/shared/QualityBadge'

export default function DashboardPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const { state, dispatch } = useSession()
  const [activeTab, setActiveTab] = useState('overview')
  const [qualityGrade] = useState<{ grade: string; score: number } | null>(null)

  useEffect(() => {
    if (!sessionId) return
    if (!state.sessionId && sessionId) {
      getSession(sessionId).then(res => {
        dispatch({
          type: 'SET_SESSION',
          payload: {
            sessionId: res.data.session_id,
            filename: res.data.filename,
            rows: res.data.rows,
            columns: res.data.columns,
            memoryMb: res.data.memory_mb,
            nullCount: res.data.null_count,
          },
        })
      }).catch(() => {})
    }
  }, [sessionId])

  useEffect(() => {
    if (state.darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [state.darkMode])

  if (!sessionId) return null

  const renderTab = () => {
    switch (activeTab) {
      case 'overview': return <DataOverview sessionId={sessionId} />
      case 'missing': return <MissingValues sessionId={sessionId} />
      case 'distributions': return <Distributions sessionId={sessionId} />
      case 'correlations': return <Correlations sessionId={sessionId} />
      case 'categories': return <Categories sessionId={sessionId} />
      case 'timeseries': return <TimeSeries sessionId={sessionId} />
      case 'preprocessing': return <Preprocessing sessionId={sessionId} />
      case 'ai': return <AIInsights sessionId={sessionId} />
      default: return null
    }
  }

  return (
    <div className="flex h-screen flex-col bg-gray-50 dark:bg-gray-900">
      <header className="flex h-12 items-center justify-between border-b border-gray-200 bg-white px-4 dark:border-gray-700 dark:bg-gray-900">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-100"
          >
            <ArrowLeft className="h-4 w-4" /> Home
          </button>
          <span className="text-gray-300 dark:text-gray-600">|</span>
          <span className="max-w-xs truncate text-sm font-medium text-gray-700 dark:text-gray-200">
            {state.filename || sessionId}
          </span>
          {qualityGrade && <QualityBadge grade={qualityGrade.grade} score={qualityGrade.score} />}
        </div>
        <button
          onClick={() => dispatch({ type: 'TOGGLE_DARK' })}
          className="rounded-lg p-1.5 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
        >
          {state.darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <Sidebar />

        <main className="flex flex-1 flex-col overflow-hidden">
          <TabNav activeTab={activeTab} onTabChange={setActiveTab} />
          <div className="flex-1 overflow-y-auto">
            {renderTab()}
          </div>
        </main>
      </div>
    </div>
  )
}
