
import { useEffect, useState } from 'react'
import Plot from 'react-plotly.js'
import { getPromotionEffect } from '../services/api'

export default function TreatmentEffects({
  dataset,
  loading = false,
  error = null
}) {
  const [analysis, setAnalysis] = useState(null)
  const [analysisLoading, setAnalysisLoading] = useState(true)
  const [analysisError, setAnalysisError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadAnalysis() {
      setAnalysisLoading(true)
      setAnalysisError('')

      try {
        const result = await getPromotionEffect()
        if (!cancelled) setAnalysis(result)
      } catch (err) {
        if (!cancelled) {
          setAnalysisError(err.message || 'Unable to load analysis.')
        }
      } finally {
        if (!cancelled) setAnalysisLoading(false)
      }
    }

    loadAnalysis()

    return () => {
      cancelled = true
    }
  }, [])

  const rows = Array.isArray(dataset?.rows)
    ? dataset.rows
    : Array.isArray(dataset?.records)
      ? dataset.records
      : []

  const getValue = (row, name) => {
    const key = Object.keys(row || {}).find(
      key => key.toLowerCase() === name.toLowerCase()
    )
    return key ? row[key] : undefined
  }

  const chartData = rows
    .map(row => ({
      price: Number(getValue(row, 'price')),
      purchase: Number(getValue(row, 'purchase'))
    }))
    .filter(row =>
      Number.isFinite(row.price) &&
      Number.isFinite(row.purchase)
    )
    .sort((a, b) => a.price - b.price)

  const previewPurchaseRate = chartData.length
    ? chartData.reduce((sum, row) => sum + row.purchase, 0) /
      chartData.length
    : null

  const formatPercent = value =>
    Number.isFinite(value) ? `${(value * 100).toFixed(2)}%` : '—'

  const formatNumber = value =>
    Number.isFinite(value) ? value.toFixed(2) : '—'

  const baseLayout = {
    autosize: true,
    margin: { l: 65, r: 25, t: 55, b: 65 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Arial, sans-serif', size: 12 },
    xaxis: { gridcolor: '#e5e7eb', zeroline: false },
    yaxis: { gridcolor: '#e5e7eb', zeroline: false }
  }

  const plotConfig = {
    responsive: true,
    displaylogo: false
  }

  const chartStyle = {
    width: '100%',
    height: '100%'
  }

  const interval = analysis?.confidence_interval_95
  const validInterval =
    Array.isArray(interval) &&
    interval.length === 2 &&
    interval.every(Number.isFinite)

  return (
    <div className="page">
      <h1>Treatment Effects</h1>
      <p>
        Analysis of promotion and purchase outcomes using the complete
        synthetic dataset. Estimates are not proof of real-world causation.
      </p>

      {(loading || analysisLoading) && (
        <p role="status">Loading analysis...</p>
      )}

      {(error || analysisError) && (
        <p role="alert">
          {typeof error === 'string' ? error : ''}
          {analysisError}
        </p>
      )}

      <div className="stats-grid">
        <div className="panel">
          <p>Analysis Observations</p>
          <h2>{analysis?.observations ?? '—'}</h2>
        </div>

        <div className="panel">
          <p>Adjusted Promotion Effect</p>
          <h2>
            {analysis
              ? `${analysis.adjusted_effect_percentage_points > 0 ? '+' : ''}${analysis.adjusted_effect_percentage_points.toFixed(2)} pp`
              : '—'}
          </h2>
        </div>

        <div className="panel">
          <p>95% Confidence Interval</p>
          <h2>
            {validInterval
              ? `${(interval[0] * 100).toFixed(2)} to ${(interval[1] * 100).toFixed(2)} pp`
              : '—'}
          </h2>
        </div>
      </div>

      <section className="panel">
        <h2>Promotion vs Control Purchase Rate</h2>
        <p>
          Observed purchase rates for customers with and without promotion.
        </p>

        {analysis && (
          <Plot
            data={[
              {
                x: ['No Promotion', 'Promotion'],
                y: [
                  analysis.control_purchase_rate * 100,
                  analysis.promotion_purchase_rate * 100
                ],
                type: 'bar',
                marker: { color: ['#64748b', '#2563eb'] },
                hovertemplate:
                  '%{x}<br>Purchase rate: %{y:.2f}%<extra></extra>'
              }
            ]}
            layout={{
              ...baseLayout,
              title: { text: 'Observed Purchase Rates' },
              height: 340,
              yaxis: {
                ...baseLayout.yaxis,
                title: { text: 'Purchase Rate (%)' },
                rangemode: 'tozero'
              }
            }}
            config={plotConfig}
            useResizeHandler
            style={chartStyle}
          />
        )}
      </section>

      <section className="panel">
        <h2>Price vs Purchase</h2>
        <p>
          Each point shows an observed record from the dataset preview.
          Purchase is coded as 0 or 1. This chart is descriptive, not causal.
        </p>

        {chartData.length > 0 ? (
          <Plot
            data={[
              {
                x: chartData.map(row => row.price),
                y: chartData.map(row => row.purchase),
                type: 'scatter',
                mode: 'markers',
                name: 'Observed purchase',
                marker: {
                  color: '#2563eb',
                  size: 8,
                  opacity: 0.7
                },
                hovertemplate:
                  'Price: %{x:.2f}<br>Purchase: %{y}<extra></extra>'
              }
            ]}
            layout={{
              ...baseLayout,
              title: { text: 'Price and Purchase Outcome' },
              height: 340,
              xaxis: {
                ...baseLayout.xaxis,
                title: { text: 'Price' }
              },
              yaxis: {
                ...baseLayout.yaxis,
                title: { text: 'Purchase (0 = No, 1 = Yes)' },
                tickmode: 'array',
                tickvals: [0, 1]
              }
            }}
            config={plotConfig}
            useResizeHandler
            style={chartStyle}
          />
        ) : (
          <p>No purchase preview data is available.</p>
        )}

        <p>
          Preview purchase rate: {formatPercent(previewPurchaseRate)}
        </p>
      </section>

      <section className="panel">
        <h2>Adjusted Promotion Analysis</h2>

        {analysis ? (
          <>
            <p>
              Adjusted estimate: {formatNumber(
                analysis.adjusted_effect_percentage_points
              )} percentage points.
            </p>
            <p>
              Promotion group: {formatPercent(
                analysis.promotion_purchase_rate
              )}
              {' · '}
              Control group: {formatPercent(
                analysis.control_purchase_rate
              )}
            </p>
            <p>
              Robust standard error: {formatNumber(
                analysis.robust_standard_error
              )}
            </p>
            <p>
              Method: adjusted linear probability model with
              heteroskedasticity-robust standard errors.
            </p>
            <p>
              Covariates: {analysis.covariates?.join(', ')}
            </p>
            <p>
              <strong>Interpretation:</strong> The adjusted estimate
              describes the promotion-associated difference in purchase
              probability after accounting for the listed variables.
              The confidence interval reflects model-based uncertainty,
              not uncertainty from unmeasured confounding.
            </p>
            <p>
              <strong>Data limitation:</strong>{' '}
              {analysis.causal_warning}
            </p>
          </>
        ) : (
          <p>
            The adjusted analysis is unavailable until the backend endpoint
            responds successfully.
          </p>
        )}
      </section>

      <section className="panel">
        <h2>Uplift and Qini Evaluation</h2>
        <p>
          These evaluations are not available yet. A valid evaluation
          requires customer-level treatment-effect predictions and
          appropriate evaluation data. No illustrative curves are shown.
        </p>
      </section>

      <section className="panel">
        <h2>Customer-Level Treatment Effects</h2>
        <p>
          Individual treatment-effect predictions have not been
          implemented yet. The adjusted promotion estimate above is a
          population-level estimate, not an individual prediction.
        </p>
      </section>
    </div>
  )
}
