
import { useEffect, useState } from 'react'
import Plot from 'react-plotly.js'
import {
  getPromotionEffect,
  getPromotionEffectDML
} from '../services/api'

export default function TreatmentEffects({
  dataset,
  loading = false,
  error = null
}) {
  const [analysis, setAnalysis] = useState(null)
  const [dmlAnalysis, setDmlAnalysis] = useState(null)
  const [analysisLoading, setAnalysisLoading] = useState(true)
  const [dmlLoading, setDmlLoading] = useState(true)
  const [analysisError, setAnalysisError] = useState('')
  const [dmlError, setDmlError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadAnalyses() {
      setAnalysisLoading(true)
      setDmlLoading(true)
      setAnalysisError('')
      setDmlError('')

      const results = await Promise.allSettled([
        getPromotionEffect(),
        getPromotionEffectDML()
      ])

      if (cancelled) return

      if (results[0].status === 'fulfilled') {
        setAnalysis(results[0].value)
      } else {
        setAnalysisError(
          results[0].reason?.message ||
          'Unable to load adjusted analysis.'
        )
      }

      if (results[1].status === 'fulfilled') {
        setDmlAnalysis(results[1].value)
      } else {
        setDmlError(
          results[1].reason?.message ||
          'Unable to load DML analysis.'
        )
      }

      setAnalysisLoading(false)
      setDmlLoading(false)
    }

    loadAnalyses()

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
    Number.isFinite(value)
      ? `${(value * 100).toFixed(2)}%`
      : '—'

  const formatNumber = value =>
    Number.isFinite(value) ? value.toFixed(2) : '—'

  const formatEffect = value =>
    Number.isFinite(value)
      ? `${value > 0 ? '+' : ''}${value.toFixed(2)} pp`
      : '—'

  const formatInterval = interval =>
    Array.isArray(interval) &&
    interval.length === 2 &&
    interval.every(Number.isFinite)
      ? `${(interval[0] * 100).toFixed(2)} to ${(interval[1] * 100).toFixed(2)} pp`
      : '—'

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

  const adjustedInterval = analysis?.confidence_interval_95
  const dmlInterval = dmlAnalysis?.confidence_interval_95

  return (
    <div className="page">
      <h1>Treatment Effects</h1>
      <p>
        Analysis of promotion and purchase outcomes using synthetic
        data. Results from these models do not prove real-world causation.
      </p>

      {(loading || analysisLoading || dmlLoading) && (
        <p role="status">Loading treatment effect analyses...</p>
      )}

      {(error || analysisError || dmlError) && (
        <div role="alert">
          {typeof error === 'string' && <p>{error}</p>}
          {analysisError && <p>Adjusted model: {analysisError}</p>}
          {dmlError && <p>DML model: {dmlError}</p>}
        </div>
      )}

      <div className="stats-grid">
        <div className="panel">
          <p>Analysis Observations</p>
          <h2>{analysis?.observations ?? dmlAnalysis?.observations ?? '—'}</h2>
        </div>

        <div className="panel">
          <p>Adjusted Linear Model</p>
          <h2>
            {formatEffect(
              analysis?.adjusted_effect_percentage_points
            )}
          </h2>
          <p>95% CI: {formatInterval(adjustedInterval)}</p>
        </div>

        <div className="panel">
          <p>DML Treatment Effect</p>
          <h2>
            {formatEffect(
              dmlAnalysis?.dml_effect_percentage_points
            )}
          </h2>
          <p>95% CI: {formatInterval(dmlInterval)}</p>
        </div>

        <div className="panel">
          <p>DML Cross-Fitting Folds</p>
          <h2>{dmlAnalysis?.cross_fitting_folds ?? '—'}</h2>
        </div>
      </div>

      <section className="panel">
        <h2>Promotion vs Control Purchase Rate</h2>
        <p>
          Observed purchase rates for customers with and without promotion.
          These are group-level observed rates, not adjusted causal effects.
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
          Each point represents a record available in the dataset preview.
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
        <h2>Adjusted Linear Probability Model</h2>

        {analysis ? (
          <>
            <p>
              <strong>Adjusted effect:</strong>{' '}
              {formatEffect(analysis.adjusted_effect_percentage_points)}
            </p>
            <p>
              <strong>95% confidence interval:</strong>{' '}
              {formatInterval(analysis.confidence_interval_95)}
            </p>
            <p>
              <strong>Robust standard error:</strong>{' '}
              {formatNumber(analysis.robust_standard_error)}
            </p>
            <p>
              <strong>Method:</strong> Adjusted linear probability model
              with heteroskedasticity-robust standard errors.
            </p>
            <p>
              <strong>Covariates:</strong>{' '}
              {analysis.covariates?.join(', ')}
            </p>
            <p>
              The estimate describes the adjusted difference in purchase
              probability associated with promotion after accounting for
              the listed variables. Unmeasured confounding may remain.
            </p>
            <p>
              <strong>Data limitation:</strong>{' '}
              {analysis.causal_warning}
            </p>
          </>
        ) : (
          <p>Adjusted linear model results are unavailable.</p>
        )}
      </section>

      <section className="panel">
        <h2>Doubly Robust DML Analysis</h2>

        {dmlAnalysis ? (
          <>
            <p>
              <strong>DML effect:</strong>{' '}
              {formatEffect(dmlAnalysis.dml_effect_percentage_points)}
            </p>
            <p>
              <strong>95% confidence interval:</strong>{' '}
              {formatInterval(dmlAnalysis.confidence_interval_95)}
            </p>
            <p>
              <strong>Standard error:</strong>{' '}
              {formatNumber(dmlAnalysis.standard_error)}
            </p>
            <p>
              <strong>Cross-fitting folds:</strong>{' '}
              {dmlAnalysis.cross_fitting_folds}
            </p>
            <p>
              <strong>Method:</strong> Cross-fitted doubly robust
              estimation using machine-learning models for the outcome
              and treatment assignment.
            </p>
            <p>
              <strong>Covariates:</strong>{' '}
              {dmlAnalysis.covariates?.join(', ')}
            </p>
            <p>
              The DML estimate uses cross-fitting and an orthogonal score
              to reduce sensitivity to nuisance-model estimation errors.
              It does not automatically eliminate unmeasured confounding
              or other model limitations.
            </p>
            <p>
              <strong>Data limitation:</strong>{' '}
              {dmlAnalysis.causal_warning}
            </p>
          </>
        ) : (
          <p>DML results are unavailable until its backend endpoint responds.</p>
        )}
      </section>

      <section className="panel">
        <h2>Method Comparison</h2>

        {analysis && dmlAnalysis ? (
          <>
            <table>
              <thead>
                <tr>
                  <th>Measure</th>
                  <th>Adjusted Linear Model</th>
                  <th>DML Model</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Estimated effect</td>
                  <td>
                    {formatEffect(
                      analysis.adjusted_effect_percentage_points
                    )}
                  </td>
                  <td>
                    {formatEffect(
                      dmlAnalysis.dml_effect_percentage_points
                    )}
                  </td>
                </tr>
                <tr>
                  <td>95% confidence interval</td>
                  <td>{formatInterval(adjustedInterval)}</td>
                  <td>{formatInterval(dmlInterval)}</td>
                </tr>
                <tr>
                  <td>Standard error</td>
                  <td>{formatNumber(analysis.robust_standard_error)}</td>
                  <td>{formatNumber(dmlAnalysis.standard_error)}</td>
                </tr>
              </tbody>
            </table>

            <p>
              Difference between point estimates:{' '}
              {formatNumber(
                Math.abs(
                  dmlAnalysis.dml_effect_percentage_points -
                  analysis.adjusted_effect_percentage_points
                )
              )} percentage points.
            </p>
            <p>
              Different methods can produce different estimates because
              they use different estimation procedures. Compare the
              assumptions, uncertainty intervals, and data limitations
              before drawing conclusions.
            </p>
          </>
        ) : (
          <p>
            The comparison will appear when both analysis endpoints
            return results.
          </p>
        )}
      </section>

      <section className="panel">
        <h2>Uplift and Qini Evaluation</h2>
        <p>
          These evaluations are not available yet. Valid evaluation
          requires customer-level treatment-effect predictions and
          appropriate evaluation data. No illustrative curves are shown.
        </p>
      </section>

      <section className="panel">
        <h2>Customer-Level Treatment Effects</h2>
        <p>
          Individual treatment-effect predictions have not been
          implemented yet. The estimates above are population-level
          estimates, not individual predictions.
        </p>
      </section>
    </div>
  )
}
