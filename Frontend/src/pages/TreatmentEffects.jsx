import Plot from 'react-plotly.js'

export default function TreatmentEffects ({ dataset }) {
  const hasPriceAndSales =
    dataset?.rows?.length > 0 &&
    dataset.columns?.some(column => column.toLowerCase() === 'price') &&
    dataset.columns?.some(column => column.toLowerCase() === 'sales')

  const chartData = hasPriceAndSales
    ? dataset.rows
        .map(row => ({
          price: Number(row.price),
          sales: Number(row.sales)
        }))
        .filter(row => Number.isFinite(row.price) && Number.isFinite(row.sales))
        .sort((a, b) => a.price - b.price)
    : []

  const upliftPreviewData =
    chartData.length > 1
      ? (() => {
          const sales = chartData.map(row => row.sales)
          const min = Math.min(...sales)
          const range = Math.max(...sales) - min || 1

          return chartData.map((row, index) => ({
            population: ((index + 1) / chartData.length) * 100,
            uplift: ((row.sales - min) / range) * 100
          }))
        })()
      : []

  const validObservationCount = chartData.length

  const averagePrice =
    validObservationCount > 0
      ? chartData.reduce((sum, row) => sum + row.price, 0) /
        validObservationCount
      : null

  const averageSales =
    validObservationCount > 0
      ? chartData.reduce((sum, row) => sum + row.sales, 0) /
        validObservationCount
      : null

  const qiniPreviewData = upliftPreviewData.map(point => ({
    population: point.population,
    model: (point.uplift * point.population) / 100,
    baseline: point.population * 0.5
  }))

  const plotLayout = {
    autosize: true,
    margin: { l: 60, r: 25, t: 25, b: 65 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Arial, sans-serif', size: 12 },
    xaxis: { gridcolor: '#e5e7eb' },
    yaxis: { gridcolor: '#e5e7eb' },
    legend: { orientation: 'h', y: -0.25 }
  }

  const plotConfig = {
    responsive: true,
    displaylogo: false
  }

  return (
    <div className='page'>
      <h1>Treatment Effects</h1>
      <p>
        Explore observed pricing and sales data and review treatment-effect
        results when the model is connected.
      </p>

      <div className='stats-grid'>
        <div className='panel'>
          <p>Valid Observations</p>
          <h2>{validObservationCount}</h2>
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

      <section className='panel'>
        <h2>Price vs Sales</h2>
        <p>
          This chart shows an observed relationship. It does not establish that
          price causes sales to change.
        </p>

        {chartData.length > 0 ? (
          <Plot
            data={[
              {
                x: chartData.map(row => row.price),
                y: chartData.map(row => row.sales),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Observed sales',
                line: { color: '#2563eb', width: 2 },
                marker: { size: 7 }
              }
            ]}
            layout={{
              ...plotLayout,
              height: 320,
              xaxis: {
                ...plotLayout.xaxis,
                title: 'Price'
              },
              yaxis: {
                ...plotLayout.yaxis,
                title: 'Sales'
              }
            }}
            config={plotConfig}
            useResizeHandler
            style={{ width: '100%' }}
          />
        ) : (
          <p>
            Upload a CSV containing valid price and sales columns to display
            this chart.
          </p>
        )}
      </section>

      <section className='panel'>
        <h2>Uplift Curve</h2>
        <p>
          Illustrative preview calculated from uploaded sales values, not a
          genuine causal uplift curve.
        </p>

        {upliftPreviewData.length > 1 ? (
          <Plot
            data={[
              {
                x: upliftPreviewData.map(p => p.population),
                y: upliftPreviewData.map(p => p.uplift),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Illustrative preview',
                line: { color: '#7c3aed', width: 2 }
              }
            ]}
            layout={{
              ...plotLayout,
              height: 320,
              xaxis: {
                ...plotLayout.xaxis,
                title: 'Customers Selected (%)',
                range: [0, 100]
              },
              yaxis: {
                ...plotLayout.yaxis,
                title: 'Normalized Sales (%)'
              }
            }}
            config={plotConfig}
            useResizeHandler
            style={{ width: '100%' }}
          />
        ) : (
          <p>
            Upload at least two valid price and sales rows to view this preview.
          </p>
        )}
      </section>

      <section className='panel'>
        <h2>Qini Curve</h2>
        <p>
          Illustrative comparison only. The actual Qini curve requires treatment
          labels, outcomes, and model predictions.
        </p>

        {qiniPreviewData.length > 1 ? (
          <Plot
            data={[
              {
                x: qiniPreviewData.map(p => p.population),
                y: qiniPreviewData.map(p => p.model),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Illustrative preview',
                line: { color: '#2563eb', width: 2 }
              },
              {
                x: qiniPreviewData.map(p => p.population),
                y: qiniPreviewData.map(p => p.baseline),
                type: 'scatter',
                mode: 'lines',
                name: 'Reference line',
                line: {
                  color: '#64748b',
                  dash: 'dash',
                  width: 2
                }
              }
            ]}
            layout={{
              ...plotLayout,
              height: 320,
              xaxis: {
                ...plotLayout.xaxis,
                title: 'Customers Selected (%)',
                range: [0, 100]
              },
              yaxis: {
                ...plotLayout.yaxis,
                title: 'Illustrative Score'
              }
            }}
            config={plotConfig}
            useResizeHandler
            style={{ width: '100%' }}
          />
        ) : (
          <p>
            Upload at least two valid price and sales rows to view this preview.
          </p>
        )}
      </section>

      <section className='panel'>
        <h2>Estimated Treatment Effect</h2>
        <p>
          The Double Machine Learning estimate will appear here when the backend
          API is connected.
        </p>
        <p>
          <strong>Status:</strong> Waiting for model results
        </p>
      </section>
    </div>
  )
}
