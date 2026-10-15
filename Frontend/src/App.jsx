import { useState } from 'react'
import DataUpload from './pages/DataUpload.jsx'
import BudgetSettings from './pages/BudgetSettings.jsx'
import Dashboard from './pages/Dashboard.jsx'
import TreatmentEffects from './pages/TreatmentEffects.jsx'
import './index.css'

export default function App () {
  const [activePage, setActivePage] = useState('Dashboard')
  const [budget, setBudget] = useState(null)
  const [dataset, setDataset] = useState(null)

  const menuItems = [
    'Dashboard',
    'Data Upload',
    'Budget Settings',
    'Treatment Effects'
  ]

  return (
    <div className='app'>
      <aside className='sidebar'>
        <h2>EconoCausal</h2>
        <p className='subtitle'>Pricing Intelligence</p>

        {menuItems.map(item => (
          <button
            key={item}
            className={`nav-item ${activePage === item ? 'active' : ''}`}
            onClick={() => setActivePage(item)}
          >
            {item}
          </button>
        ))}
      </aside>

      <main className='main-content'>
        <header className='topbar'>
          <div>
            <h1>{activePage}</h1>
            <p>Dynamic Pricing via Double Machine Learning</p>
          </div>
          <span className='status'>Frontend Preview</span>
        </header>

        {activePage === 'Dashboard' && (
          <Dashboard budget={budget} dataset={dataset} />
        )}

        {activePage === 'Data Upload' && (
          <DataUpload dataset={dataset} onDatasetLoaded={setDataset} />
        )}

        {activePage === 'Budget Settings' && (
          <BudgetSettings budget={budget} onSave={setBudget} />
        )}

        {activePage === 'Treatment Effects' && (
          <TreatmentEffects dataset={dataset} />
        )}
      </main>
    </div>
  )
}
