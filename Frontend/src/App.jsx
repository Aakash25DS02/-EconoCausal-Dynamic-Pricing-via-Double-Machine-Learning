
import { useState, useEffect, useCallback, lazy, Suspense } from 'react'
import DataUpload from './pages/DataUpload.jsx'
import BudgetSettings from './pages/BudgetSettings.jsx'
import BudgetAllocation from './pages/BudgetAllocation.jsx'
import Dashboard from './pages/Dashboard.jsx'
import {
  getHealth,
  getDataSummary,
  getDataPreview
} from './services/api.js'
import './index.css'

const TreatmentEffects = lazy(
  () => import('./pages/TreatmentEffects.jsx')
)

export default function App() {
  const [activePage, setActivePage] = useState('Dashboard')
  const [budget, setBudget] = useState(null)
  const [dataset, setDataset] = useState(null)
  const [apiStatus, setApiStatus] = useState('Checking...')
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)

  const loadBackendData = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const health = await getHealth()

      if (health.status !== 'ok') {
        throw new Error('Backend health check failed.')
      }

      const [summaryData, previewData] = await Promise.all([
        getDataSummary(),
        getDataPreview()
      ])

      if (
        !summaryData ||
        !Array.isArray(summaryData.columns) ||
        !previewData
      ) {
        throw new Error('The backend returned an invalid dataset response.')
      }

      setApiStatus('Connected')
      setSummary(summaryData)

      setDataset({
        ...summaryData,
        records: Array.isArray(previewData.records)
          ? previewData.records
          : []
      })

      setLastUpdated(new Date())
    } catch (err) {
      setApiStatus('Disconnected')
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to connect to the backend.'
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadBackendData()
  }, [loadBackendData])

  const menuItems = [
    'Dashboard',
    'Data Upload',
    'Budget Settings',
    'Budget Allocation',
    'Treatment Effects'
  ]

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">
            <span>EC</span>
          </div>
          <div className="brand-copy">
            <h2>EconoCausal</h2>
            <p className="subtitle">Pricing Intelligence</p>
          </div>
        </div>

        <p className="subtitle">Pricing Intelligence</p>

        {menuItems.map(item => (
          <button
            key={item}
            className={`nav-item ${
              activePage === item ? 'active' : ''
            }`}
            onClick={() => setActivePage(item)}
          >
            {item}
          </button>
        ))}
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>{activePage}</h1>
            <p>Dynamic Pricing via Double Machine Learning</p>
          </div>

          <span className="status">
            Backend: {apiStatus}
          </span>
        </header>

        {error && activePage !== 'Dashboard' && (
          <div role="alert" className="panel">
            Backend connection error: {error}
          </div>
        )}

        {activePage === 'Dashboard' && (
          <Dashboard
            budget={budget}
            dataset={dataset}
            summary={summary}
            loading={loading}
            error={error}
            apiStatus={apiStatus}
            lastUpdated={lastUpdated}
            onRefresh={loadBackendData}
          />
        )}

        {activePage === 'Data Upload' && (
          <DataUpload
            dataset={dataset}
            onDatasetLoaded={setDataset}
          />
        )}

        {activePage === 'Budget Settings' && (
          <BudgetSettings
            budget={budget}
            onSave={setBudget}
          />
        )}

        {activePage === 'Budget Allocation' && (
          <BudgetAllocation budget={budget} />
        )}

        {activePage === 'Treatment Effects' && (
          <Suspense
            fallback={
              <p role="status">
                Loading Treatment Effects page...
              </p>
            }
          >
            <TreatmentEffects
              dataset={dataset}
              loading={loading}
              error={error}
            />
          </Suspense>
        )}
      </main>
    </div>
  )
}
