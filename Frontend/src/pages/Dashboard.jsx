
export default function Dashboard({
  budget,
  dataset,
  summary,
  loading,
  error,
  apiStatus,
  lastUpdated,
  onRefresh
}) {
  const money = value =>
    typeof value === 'number' && Number.isFinite(value)
      ? `₹${value.toLocaleString('en-IN', {
          maximumFractionDigits: 2
        })}`
      : '—'

  const purchaseRate =
    typeof summary?.purchase_rate === 'number'
      ? `${(summary.purchase_rate * 100).toFixed(1)}%`
      : '—'

  const averageDiscount =
    typeof summary?.average_discount === 'number'
      ? `${(summary.average_discount * 100).toFixed(2)}%`
      : '—'

  const columns = Array.isArray(summary?.columns)
    ? summary.columns
    : []

  const missingValues = summary?.missing_values &&
    typeof summary.missing_values === 'object'
      ? Object.values(summary.missing_values).reduce(
          (total, count) =>
            total + (typeof count === 'number' ? count : 0),
          0
        )
      : 0

  const formattedLastUpdated = lastUpdated
    ? lastUpdated.toLocaleString('en-IN', {
        dateStyle: 'medium',
        timeStyle: 'short'
      })
    : 'Not updated yet'

  return (
    <>
      <div className="welcome">
        <div>
          <h2>Welcome to EconoCausal</h2>
          <p>
            Analyze pricing data and explore customer purchasing
            patterns using your connected dataset.
          </p>
        </div>

        <button
          type="button"
          className="refresh-button"
          onClick={onRefresh}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : '↻ Refresh Data'}
        </button>
      </div>

      <section className="dashboard-update panel">
        <div>
          <strong>Backend Status</strong>
          <p className={`connection-status ${
            apiStatus === 'Connected' ? 'connected' : 'disconnected'
          }`}>
            {apiStatus}
          </p>
        </div>

        <div>
          <strong>Last Updated</strong>
          <p>{formattedLastUpdated}</p>
        </div>
      </section>

      {loading && (
        <p role="status" className="loading-message">
          Loading the latest backend dataset...
        </p>
      )}

      {error && (
        <div role="alert" className="panel error-message">
          <strong>Unable to load backend data</strong>
          <p>{error}</p>
          <p>Please check the backend connection and try again.</p>
        </div>
      )}

      <div className="stats-grid">
        <div className="stat-card">
          <p>Backend Dataset</p>
          <h2>
            {summary ? 'Connected' : loading ? 'Loading...' : 'Unavailable'}
          </h2>
        </div>

        <div className="stat-card">
          <p>Total Records</p>
          <h2>
            {typeof summary?.rows === 'number'
              ? summary.rows.toLocaleString('en-IN')
              : '—'}
          </h2>
        </div>

        <div className="stat-card">
          <p>Average Price</p>
          <h2>{money(summary?.average_price)}</h2>
        </div>

        <div className="stat-card">
          <p>Purchase Rate</p>
          <h2>{purchaseRate}</h2>
        </div>

        <div className="stat-card">
          <p>Average Discount</p>
          <h2>{averageDiscount}</h2>
        </div>

        <div className="stat-card">
          <p>Budget</p>
          <h2>
            {budget !== null && budget !== undefined
              ? money(budget)
              : 'Not Set'}
          </h2>
        </div>
      </div>

      <section className="panel">
        <h2>Dataset Information</h2>

        {summary ? (
          <>
            <p>Rows: {summary.rows ?? '—'}</p>
            <p>Columns: {columns.length}</p>
            <p>Columns: {columns.join(', ') || 'No columns available'}</p>
            <p>Missing values: {missingValues}</p>
            <p>
              Preview records loaded:{' '}
              {Array.isArray(dataset?.records)
                ? dataset.records.length
                : 0}
            </p>
          </>
        ) : (
          <p>
            Backend dataset information is not currently available.
            Use Refresh Data to try again.
          </p>
        )}
      </section>

      <section className="panel">
        <h2>Getting Started</h2>
        <p>1. Review the connected pricing dataset.</p>
        <p>2. Configure your pricing budget.</p>
        <p>3. Explore treatment effects when model results are available.</p>
      </section>
    </>
  )
}
