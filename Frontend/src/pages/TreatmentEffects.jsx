import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts'

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
          const minSales = Math.min(...chartData.map(row => row.sales))
          const maxSales = Math.max(...chartData.map(row => row.sales))
          const range = maxSales - minSales || 1

          return chartData.map((row, index) => ({
            population: Number(
              (((index + 1) / chartData.length) * 100).toFixed(1)
            ),
            uplift: Number((((row.sales - minSales) / range) * 100).toFixed(2))
          }))
        })()
      : []

  const qiniPreviewData =
    chartData.length > 1
      ? (() => {
          const minSales = Math.min(...chartData.map(row => row.sales))
          const maxSales = Math.max(...chartData.map(row => row.sales))
          const range = maxSales - minSales || 1

          return chartData.map((row, index) => {
            const population = ((index + 1) / chartData.length) * 100

            const normalizedSales = (row.sales - minSales) / range

            return {
              population: Number(population.toFixed(1)),
              model: Number((normalizedSales * population).toFixed(2)),
              baseline: Number((population * 0.5).toFixed(2))
            }
          })
        })()
      : []

  return (
    <div className='page'>
      <h1>Treatment Effects</h1>
      <p>
        Explore the relationship between pricing and sales, and review estimated
        effects when model results become available.
      </p>

      <section className='panel'>
        <h2>Price vs Sales</h2>
        <p>
          This chart shows the observed relationship in your uploaded data. It
          does not establish that price causes sales to change.
        </p>

        {chartData.length > 0 ? (
          <div style={{ width: '100%', height: 320 }}>
            <ResponsiveContainer width='100%' height='100%'>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray='3 3' />
                <XAxis
                  dataKey='price'
                  type='number'
                  label={{
                    value: 'Price',
                    position: 'insideBottom',
                    offset: -5
                  }}
                />
                <YAxis
                  label={{
                    value: 'Sales',
                    angle: -90,
                    position: 'insideLeft'
                  }}
                />
                <Tooltip />
                <Legend />
                <Line
                  type='monotone'
                  dataKey='sales'
                  name='Observed sales'
                  stroke='#2563eb'
                  strokeWidth={2}
                  dot
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p>
            Upload a CSV containing columns named price and sales to display
            this chart.
          </p>
        )}
      </section>

      <section className='panel'>
        <h2>Uplift Curve</h2>
        <p>
          Data-dependent preview based on uploaded sales values. This is not an
          estimated causal uplift curve.
        </p>

        <div style={{ width: '100%', height: 320 }}>
          <ResponsiveContainer width='100%' height='100%'>
            <LineChart data={upliftPreviewData}>
              <CartesianGrid strokeDasharray='3 3' />
              <XAxis
                dataKey='population'
                type='number'
                domain={[0, 100]}
                label={{
                  value: 'Customers Selected (%)',
                  position: 'insideBottom',
                  offset: -5
                }}
              />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type='monotone'
                dataKey='uplift'
                name='Illustrative uplift'
                stroke='#7c3aed'
                strokeWidth={2}
                dot
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className='panel'>
        <h2>Qini Curve</h2>
        <p>
          Data-dependent preview compared with a reference line. This is not a
          statistically calculated Qini curve.
        </p>

        <div style={{ width: '100%', height: 320 }}>
          <ResponsiveContainer width='100%' height='100%'>
            <LineChart data={qiniPreviewData}>
              <CartesianGrid strokeDasharray='3 3' />
              <XAxis
                dataKey='population'
                type='number'
                domain={[0, 100]}
                label={{
                  value: 'Customers Selected (%)',
                  position: 'insideBottom',
                  offset: -5
                }}
              />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type='monotone'
                dataKey='model'
                name='Illustrative model'
                stroke='#2563eb'
                strokeWidth={2}
                dot
              />
              <Line
                type='monotone'
                dataKey='baseline'
                name='Illustrative baseline'
                stroke='#64748b'
                strokeDasharray='5 5'
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className='panel'>
        <h2>Estimated Treatment Effect</h2>
        <p>
          The Double Machine Learning model's estimated price effect will appear
          here when its results are connected.
        </p>
        <p>
          <strong>Status:</strong> Waiting for model results
        </p>
      </section>
    </div>
  )
}
