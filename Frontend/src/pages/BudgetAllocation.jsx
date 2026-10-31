import { useEffect, useMemo, useState } from 'react'
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from 'recharts'
import { optimizeBudgetAllocation } from '../services/api.js'

const COLORS = [
  '#2563eb',
  '#7c3aed',
  '#0d9488',
  '#ea580c',
  '#0891b2',
  '#64748b'
]

function formatCurrency (value) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2
  }).format(Number(value) || 0)
}

function formatDiscount (value) {
  return `${(Number(value) * 100).toFixed(0)}%`
}

export default function BudgetAllocation ({ budget }) {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedDiscount, setSelectedDiscount] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')

  const hasBudget = Number.isFinite(Number(budget)) && Number(budget) > 0

  useEffect(() => {
    if (!hasBudget) {
      setResult(null)
      setError(null)
      return
    }

    let isActive = true

    async function loadAllocation () {
      setLoading(true)
      setError(null)
      setResult(null)

      try {
        const data = await optimizeBudgetAllocation(budget)

        if (isActive) {
          setResult(data)
        }
      } catch (err) {
        if (isActive) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to generate budget allocation.'
          )
        }
      } finally {
        if (isActive) {
          setLoading(false)
        }
      }
    }

    loadAllocation()

    return () => {
      isActive = false
    }
  }, [budget, hasBudget])

  const allocationData = useMemo(() => {
    if (!result?.allocations) return []

    return result.allocations
  }, [result])

  const discountSummary = useMemo(() => {
    const groups = new Map()

    allocationData.forEach(item => {
      const discount = Number(item.recommended_discount)
      const key = discount.toFixed(2)

      if (!groups.has(key)) {
        groups.set(key, {
          discount,
          customers: 0,
          expectedSpend: 0,
          expectedPurchases: 0
        })
      }

      const group = groups.get(key)
      group.customers += 1
      group.expectedSpend += Number(item.expected_discount_spend)
      group.expectedPurchases += Number(item.predicted_purchase_probability)
    })

    return Array.from(groups.values())
      .sort((a, b) => a.discount - b.discount)
      .map((group, index) => ({
        ...group,
        name: formatDiscount(group.discount),
        color: COLORS[index % COLORS.length]
      }))
  }, [allocationData])

  const filteredAllocations = useMemo(() => {
    return allocationData.filter(item => {
      const matchesDiscount =
        selectedDiscount === 'all' ||
        Number(item.recommended_discount).toFixed(2) === selectedDiscount

      const matchesSearch = String(item.customer_id)
        .toLowerCase()
        .includes(searchTerm.toLowerCase())

      return matchesDiscount && matchesSearch
    })
  }, [allocationData, selectedDiscount, searchTerm])

  const groupedDiscountSummary = useMemo(() => {
    const ranges = [
      { name: '0–5%', min: 0, max: 0.05 },
      { name: '6–10%', min: 0.06, max: 0.1 },
      { name: '11–15%', min: 0.11, max: 0.15 },
      { name: '16–20%', min: 0.16, max: 0.2 },
      { name: '21–25%', min: 0.21, max: 0.25 },
      { name: '26–30%', min: 0.26, max: 0.3 },
      { name: '31–35%', min: 0.31, max: 0.35 }
    ]

    return ranges.map((range, index) => {
      const matching = allocationData.filter(item => {
        const discount = Number(item.recommended_discount)
        return discount >= range.min && discount <= range.max
      })

      return {
        name: range.name,
        customers: matching.length,
        expectedSpend: matching.reduce(
          (sum, item) => sum + Number(item.expected_discount_spend),
          0
        ),
        color: COLORS[index]
      }
    })
  }, [allocationData])

  if (!hasBudget) {
    return (
      <section className='panel'>
        <h2>Budget Allocation</h2>
        <p>
          Please save a campaign budget in Budget Settings before generating the
          allocation plan.
        </p>
      </section>
    )
  }

  if (loading) {
    return (
      <section className='panel'>
        <h2>Budget Allocation</h2>
        <p role='status'>
          Generating model-based budget allocation. Please wait...
        </p>
      </section>
    )
  }

  if (error) {
    return (
      <section className='panel'>
        <h2>Budget Allocation</h2>
        <p role='alert'>Unable to generate allocation: {error}</p>
        <p>Check that the backend is running and try again.</p>
        <button type='button' onClick={() => setSelectedDiscount('all')}>
          Reset discount filter
        </button>
      </section>
    )
  }

  if (!result) {
    return null
  }
  const chartData = groupedDiscountSummary.filter(
    group => group.expectedSpend > 0
  )

  return (
    <div className='page'>
      <h1>Budget Allocation</h1>
      <p>
        View customer-level discount recommendations generated by the backend
        allocation model.
      </p>

      <p role='note'>
        <strong>Model information:</strong> {result.method}. These are
        model-based estimates from the available dataset, not guaranteed sales
        or profit outcomes.
      </p>

      <div className='stats-grid'>
        <section className='panel'>
          <h3>Total Budget</h3>
          <h2>{formatCurrency(result.budget)}</h2>
        </section>

        <section className='panel'>
          <h3>Expected Discount Spend</h3>
          <h2>{formatCurrency(result.expected_discount_spend)}</h2>
        </section>

        <section className='panel'>
          <h3>Remaining Budget</h3>
          <h2>{formatCurrency(result.remaining_budget)}</h2>
        </section>

        <section className='panel'>
          <h3>Budget Utilization</h3>
          <h2>{result.budget_utilization_percent}%</h2>
        </section>
      </div>

      <div className='stats-grid'>
        <section className='panel'>
          <h3>Baseline Expected Purchases</h3>
          <h2>{result.baseline_expected_purchases}</h2>
        </section>

        <section className='panel'>
          <h3>Recommended Expected Purchases</h3>
          <h2>{result.recommended_expected_purchases}</h2>
        </section>

        <section className='panel'>
          <h3>Expected Purchase Improvement</h3>
          <h2>{result.expected_purchase_improvement}</h2>
        </section>

        <section className='panel'>
          <h3>Customers Analyzed</h3>
          <h2>{result.customer_count}</h2>
        </section>
      </div>

      <section className='panel'>
        <h2>Budget Distribution by Discount Level</h2>
        <p>
          Distribution of estimated discount expenditure across the recommended
          discount levels.
        </p>

        <div style={{ width: '100%', height: 320 }}>
          <ResponsiveContainer width='100%' height='100%'>
            <PieChart>
              <Pie
                data={chartData}
                dataKey='expectedSpend'
                nameKey='name'
                cx='50%'
                cy='50%'
                outerRadius={100}
                label={({ name }) => name}
              >
                {chartData.map(item => (
                  <Cell key={item.name} fill={item.color} />
                ))}
              </Pie>
              <Tooltip formatter={value => formatCurrency(value)} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className='panel'>
        <h2>Customer Allocation by Discount Level</h2>
        <p>Number of customers assigned to each recommended discount level.</p>

        <div style={{ width: '100%', height: 320 }}>
          <ResponsiveContainer width='100%' height='100%'>
            <BarChart data={discountSummary}>
              <CartesianGrid strokeDasharray='3 3' />
              <XAxis dataKey='name' />
              <YAxis />
              <Tooltip />
              <Bar
                dataKey='customers'
                name='Number of Customers'
                fill='#2563eb'
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className='panel'>
        <h2>Customer Allocation Details</h2>
        <p>
          Individual discount recommendations and predicted purchase
          probabilities returned by the backend.
        </p>

        <div
          style={{
            display: 'flex',
            gap: '12px',
            flexWrap: 'wrap',
            marginBottom: '16px'
          }}
        >
          <input
            type='text'
            placeholder='Search customer ID'
            value={searchTerm}
            onChange={event => setSearchTerm(event.target.value)}
          />

          <select
            value={selectedDiscount}
            onChange={event => setSelectedDiscount(event.target.value)}
          >
            <option value='all'>All discount levels</option>
            {discountSummary.map(group => (
              <option key={group.name} value={group.discount.toFixed(2)}>
                {group.name} discount
              </option>
            ))}
          </select>
        </div>

        <p>
          Showing {filteredAllocations.length} of {allocationData.length}{' '}
          customers.
        </p>

        <div
          style={{
            overflowX: 'auto',
            maxHeight: 500,
            width: '100%'
          }}
        >
          <table
            style={{
              minWidth: '1050px',
              width: '100%',
              whiteSpace: 'nowrap'
            }}
          >
            <thead>
              <tr>
                <th>Customer ID</th>
                <th>Price</th>
                <th>Recommended Discount</th>
                <th>Predicted Purchase Probability</th>
                <th>Expected Discount Spend</th>
              </tr>
            </thead>

            <tbody>
              {filteredAllocations.map(item => (
                <tr key={item.customer_id}>
                  <td>{item.customer_id}</td>
                  <td>{formatCurrency(item.price)}</td>
                  <td>{formatDiscount(item.recommended_discount)}</td>
                  <td>
                    {(
                      Number(item.predicted_purchase_probability) * 100
                    ).toFixed(2)}
                    %
                  </td>
                  <td>{formatCurrency(item.expected_discount_spend)}</td>
                </tr>
              ))}

              {filteredAllocations.length === 0 && (
                <tr>
                  <td colSpan='5'>No customers match the selected filters.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className='panel'>
        <h2>Allocation Summary</h2>
        <p>
          <strong>Budget check:</strong>{' '}
          {Number(result.expected_discount_spend) <= Number(result.budget)
            ? 'Expected discount spend is within the saved budget.'
            : 'Expected discount spend exceeds the saved budget.'}
        </p>

        <p role='note'>{result.note}</p>
      </section>
    </div>
  )
}
