
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'

export default function TreatmentEffects({ dataset }) {
  const hasPriceAndSales =
    dataset?.rows?.length > 0 &&
    dataset.columns?.some(
      (column) => column.toLowerCase() === 'price'
    ) &&
    dataset.columns?.some(
      (column) => column.toLowerCase() === 'sales'
    )

  const chartData = hasPriceAndSales
    ? dataset.rows
        .map((row) => ({
          price: Number(row.price),
          sales: Number(row.sales),
        }))
        .filter(
          (row) =>
            Number.isFinite(row.price) &&
            Number.isFinite(row.sales)
        )
        .sort((a, b) => a.price - b.price)
    : []

  return (
    <div className="page">
      <h1>Treatment Effects</h1>
      <p>
        Explore the relationship between pricing and sales,
        and review estimated effects when model results become available.
      </p>

      <section className="panel">
        <h2>Price vs Sales</h2>
        <p>
          This chart shows the observed relationship in your uploaded data.
          It does not establish that price causes sales to change.
        </p>

        {chartData.length > 0 ? (
          <div style={{ width: '100%', height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="price"
                  type="number"
                  label={{
                    value: 'Price',
                    position: 'insideBottom',
                    offset: -5,
                  }}
                />
                <YAxis
                  label={{
                    value: 'Sales',
                    angle: -90,
                    position: 'insideLeft',
                  }}
                />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="sales"
                  name="Observed sales"
                  stroke="#2563eb"
                  strokeWidth={2}
                  dot
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p>
            Upload a CSV containing columns named price and sales
            to display this chart.
          </p>
        )}
      </section>

      <section className="panel">
        <h2>Estimated Treatment Effect</h2>
        <p>
          The Double Machine Learning model's estimated price effect
          will appear here when its results are connected.
        </p>
        <p>
          <strong>Status:</strong> Waiting for model results
        </p>
      </section>
    </div>
  )
}
