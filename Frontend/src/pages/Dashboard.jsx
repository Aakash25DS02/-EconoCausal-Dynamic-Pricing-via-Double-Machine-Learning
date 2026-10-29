
export default function Dashboard({
  budget,
  dataset,
  summary,
  loading
}) {
  const money = value =>
    typeof value === 'number'
      ? `₹${value.toLocaleString('en-IN', {
          maximumFractionDigits: 2
        })}`
      : '—'

  return (
    <>
      <div className="welcome">
        <h2>Welcome to EconoCausal</h2>
        <p>
          Analyze pricing data and explore customer purchasing
          patterns using your connected dataset.
        </p>
      </div>

      {loading && (
        <p role="status">Loading backend dataset...</p>
      )}

      <div className="stats-grid">
        <div className="stat-card">
          <p>Backend Dataset</p>
          <h2>
            {summary
              ? 'Connected'
              : loading
                ? 'Loading...'
                : 'Unavailable'}
          </h2>
        </div>

        <div className="stat-card">
          <p>Total Records</p>
          <h2>
            {summary
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
          <h2>
            {typeof summary?.purchase_rate === 'number'
              ? `${(summary.purchase_rate * 100).toFixed(1)}%`
              : '—'}
          </h2>
        </div>

        <div className="stat-card">
          <p>Average Discount</p>
          <h2>
            {typeof summary?.average_discount === 'number'
              ? `${(summary.average_discount * 100).toFixed(2)}%`
              : '—'}
          </h2>
        </div>

        <div className="stat-card">
          <p>Budget</p>
          <h2>
            {budget !== null
              ? money(budget)
              : 'Not Set'}
          </h2>
        </div>
      </div>

      <section className="panel">
        <h2>Dataset Information</h2>

        {summary ? (
          <>
            <p>Rows: {summary.rows}</p>
            <p>Columns: {summary.columns.length}</p>
            <p>
              Columns: {summary.columns.join(', ')}
            </p>
            <p>
              Missing values:{' '}
              {Object.values(summary.missing_values)
                .reduce((total, count) => total + count, 0)}
            </p>
            <p>
              Preview records loaded: {
                Array.isArray(dataset?.records)
                  ? dataset.records.length
                  : 0
              }
            </p>
          </>
        ) : (
          <p>
            Backend dataset information is not currently available.
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
