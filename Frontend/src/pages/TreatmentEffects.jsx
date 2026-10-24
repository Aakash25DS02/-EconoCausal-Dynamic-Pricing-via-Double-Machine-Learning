import Plot from 'react-plotly.js'

export default function TreatmentEffects ({
  dataset,
  loading = false,
  error = null
}) {
  // Find CSV columns without depending on capitalization.
  const getValue = (row, columnName) => {
    const key = Object.keys(row || {}).find(
      key => key.toLowerCase() === columnName.toLowerCase()
    )
    return key ? row[key] : undefined
  }

  const rows = Array.isArray(dataset?.rows) ? dataset.rows : []

  const chartData = rows
    .map(row => ({
      price: Number(getValue(row, 'price')),
      sales: Number(getValue(row, 'sales'))
    }))
    .filter(row => Number.isFinite(row.price) && Number.isFinite(row.sales))
    .sort((a, b) => a.price - b.price)

  const count = chartData.length

  const averagePrice = count
    ? chartData.reduce((sum, row) => sum + row.price, 0) / count
    : null

  const averageSales = count
    ? chartData.reduce((sum, row) => sum + row.sales, 0) / count
    : null

  // Illustrative preview only — not a causal uplift calculation.
  const sales = chartData.map(row => row.sales)
  const minSales = count ? Math.min(...sales) : 0
  const salesRange = count ? Math.max(...sales) - minSales || 1 : 1

  const upliftPreview =
    count > 1
      ? chartData.map((row, index) => ({
          population: ((index + 1) / count) * 100,
          uplift: ((row.sales - minSales) / salesRange) * 100
        }))
      : []

  // Illustrative score only — not a genuine Qini curve.
  const qiniPreview = upliftPreview.map(point => ({
    population: point.population,
    model: (point.uplift * point.population) / 100,
    baseline: point.population * 0.5
  }))

  // Accept customer results when provided by the backend.

  const customerResults =
    dataset?.treatmentEffects ??
    dataset?.customerEffects ??
    dataset?.treatment_effects ??
    dataset?.customer_results ??
    []

  const hasCustomerResults =
    Array.isArray(customerResults) && customerResults.length > 0

  // Show uploaded customer records when model predictions are not available.
  // These are observed records, NOT treatment-effect predictions.
  const displayCustomers = hasCustomerResults
    ? customerResults
    : Array.isArray(dataset?.rows)
    ? dataset.rows
    : []

  const getField = (row, names) => {
    const key = Object.keys(row || {}).find(key =>
      names.includes(key.toLowerCase())
    )
    return key ? row[key] : undefined
  }

  const displayValue = value => {
    if (value === null || value === undefined || value === '') {
      return '—'
    }

    const number = Number(value)
    return Number.isFinite(number) ? number.toFixed(2) : String(value)
  }

  const baseLayout = {
    autosize: true,
    margin: { l: 65, r: 25, t: 55, b: 80 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Arial, sans-serif', size: 12 },
    hovermode: 'closest',
    xaxis: {
      gridcolor: '#e5e7eb',
      zeroline: false
    },
    yaxis: {
      gridcolor: '#e5e7eb',
      zeroline: false
    },
    legend: {
      orientation: 'h',
      y: -0.25
    }
  }

  const plotConfig = {
    responsive: true,
    displaylogo: false
  }

  const chartStyle = {
    width: '100%',
    height: '100%'
  }

  return (
    <div className='page'>
      {loading && <p role='status'>Loading treatment-effect data...</p>}

      {error && (
        <p role='alert'>
          Unable to load treatment-effect data:{' '}
          {typeof error === 'string' ? error : 'Please try again.'}
        </p>
      )}
      <h1>Treatment Effects</h1>
      <p>
        Explore observed pricing and sales data, model evaluation previews, and
        customer-level treatment-effect predictions.
      </p>

      {/* Summary cards */}
      <div className='stats-grid'>
        <div className='panel'>
          <p>Valid Observations</p>
          <h2>{count}</h2>
        </div>

        <div className='panel'>
          <p>Average Price</p>
          <h2>{averagePrice === null ? '—' : averagePrice.toFixed(2)}</h2>
        </div>

        <div className='panel'>
          <p>Average Sales</p>
          <h2>{averageSales === null ? '—' : averageSales.toFixed(2)}</h2>
        </div>
      </div>

      {/* Price vs Sales */}
      <section className='panel'>
        <h2>Price vs Sales</h2>
        <p>
          Observed relationship between price and sales. This chart does not
          establish causation.
        </p>

        {count > 0 ? (
          <Plot
            data={[
              {
                x: chartData.map(row => row.price),
                y: chartData.map(row => row.sales),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Observed sales',
                line: { color: '#2563eb', width: 2 },
                marker: { size: 7 },
                hovertemplate:
                  'Price: %{x:.2f}<br>Sales: %{y:.2f}<extra></extra>'
              }
            ]}
            layout={{
              ...baseLayout,
              title: { text: 'Price and Sales Relationship' },
              height: 340,
              xaxis: { ...baseLayout.xaxis, title: { text: 'Price' } },
              yaxis: { ...baseLayout.yaxis, title: { text: 'Sales' } }
            }}
            config={plotConfig}
            useResizeHandler
            style={chartStyle}
          />
        ) : (
          <p>Upload a CSV with valid Price and Sales columns.</p>
        )}
      </section>

      {/* Uplift Curve */}
      <section className='panel'>
        <h2>Uplift Curve</h2>
        <p>
          Preview based on normalized observed sales. Actual uplift requires
          treatment labels, outcomes, and model predictions.
        </p>

        {upliftPreview.length > 1 ? (
          <Plot
            data={[
              {
                x: upliftPreview.map(point => point.population),
                y: upliftPreview.map(point => point.uplift),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Illustrative preview',
                line: { color: '#7c3aed', width: 3 },
                marker: { size: 6 },
                hovertemplate:
                  'Customers selected: %{x:.1f}%<br>' +
                  'Normalized sales: %{y:.2f}%<extra></extra>'
              }
            ]}
            layout={{
              ...baseLayout,
              title: { text: 'Uplift Curve — Illustrative Preview' },
              height: 350,
              xaxis: {
                ...baseLayout.xaxis,
                title: { text: 'Customers Selected (%)' },
                range: [0, 100]
              },
              yaxis: {
                ...baseLayout.yaxis,
                title: { text: 'Normalized Sales (%)' }
              }
            }}
            config={plotConfig}
            useResizeHandler
            style={chartStyle}
          />
        ) : (
          <p>
            At least two valid Price and Sales rows are required for this
            preview.
          </p>
        )}
      </section>

      {/* Qini Curve */}
      <section className='panel'>
        <h2>Qini Curve</h2>
        <p>
          Illustrative comparison, not a model evaluation. A genuine Qini curve
          requires treatment assignments, outcomes, and individual
          treatment-effect predictions.
        </p>

        {qiniPreview.length > 1 ? (
          <Plot
            data={[
              {
                x: qiniPreview.map(point => point.population),
                y: qiniPreview.map(point => point.model),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Illustrative model score',
                line: { color: '#2563eb', width: 3 },
                hovertemplate:
                  'Customers selected: %{x:.1f}%<br>' +
                  'Illustrative score: %{y:.2f}<extra></extra>'
              },
              {
                x: qiniPreview.map(point => point.population),
                y: qiniPreview.map(point => point.baseline),
                type: 'scatter',
                mode: 'lines',
                name: 'Illustrative reference',
                line: { color: '#64748b', dash: 'dash', width: 2 },
                hovertemplate:
                  'Customers selected: %{x:.1f}%<br>' +
                  'Reference score: %{y:.2f}<extra></extra>'
              }
            ]}
            layout={{
              ...baseLayout,
              title: { text: 'Qini Curve — Illustrative Preview' },
              height: 350,
              xaxis: {
                ...baseLayout.xaxis,
                title: { text: 'Customers Selected (%)' },
                range: [0, 100]
              },
              yaxis: {
                ...baseLayout.yaxis,
                title: { text: 'Illustrative Score' }
              }
            }}
            config={plotConfig}
            useResizeHandler
            style={chartStyle}
          />
        ) : (
          <p>
            At least two valid Price and Sales rows are required for this
            preview.
          </p>
        )}
      </section>

      {/* Customer-level treatment effects */}
      <section className='panel'>
        <h2>Customer-Level Treatment Effects</h2>
        <p>Individual treatment-effect predictions returned by the model.</p>

        {displayCustomers.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className='results-table'>
              <thead>
                <tr>
                  <th>Customer ID</th>
                  <th>Treatment Effect</th>
                  <th>Treatment Prediction</th>
                  <th>Control Prediction</th>
                </tr>
              </thead>

              <tbody>
                {displayCustomers.map((customer, index) => (
                  <tr key={index}>
                    <td>
                      {getField(customer, [
                        'customer_id',
                        'customerid',
                        'id'
                      ]) ?? `Row ${index + 1}`}
                    </td>
                    <td>
                      {hasCustomerResults
                        ? displayValue(
                            getField(customer, [
                              'treatment_effect',
                              'treatmenteffect',
                              'uplift'
                            ])
                          )
                        : 'Not calculated'}
                    </td>
                    <td>
                      {displayValue(
                        getField(customer, [
                          'treatment_prediction',
                          'treatmentprediction',
                          'mu1'
                        ])
                      )}
                    </td>
                    <td>
                      {displayValue(
                        getField(customer, [
                          'control_prediction',
                          'controlprediction',
                          'mu0'
                        ])
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>
            No customer-level predictions are available. Connect the model API
            to display results here.
          </p>
        )}
      </section>

      {/* Model status */}
      <section className='panel'>
        <h2>Model Status</h2>
        <p>
          <strong>Status:</strong>{' '}
          {hasCustomerResults
            ? 'Customer predictions available'
            : 'Waiting for model results'}
        </p>
      </section>
    </div>
  )
}
