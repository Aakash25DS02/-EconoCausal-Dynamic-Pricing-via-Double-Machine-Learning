import { useEffect, useState } from 'react'

import Papa from 'papaparse'

export default function DataUpload ({ dataset, onDatasetLoaded }) {
  const [fileName, setFileName] = useState('')
  const [columns, setColumns] = useState([])
  const [rows, setRows] = useState([])
  const [missingValues, setMissingValues] = useState({})
  const [statistics, setStatistics] = useState({})
  const [error, setError] = useState('')
  const [rowCount, setRowCount] = useState(0)

  
useEffect(() => {
  if (!dataset) return

  // Support both uploaded CSV data and backend API data.
  const dataRows = Array.isArray(dataset.rows)
    ? dataset.rows
    : Array.isArray(dataset.records)
      ? dataset.records
      : []

  const dataColumns = Array.isArray(dataset.columns)
    ? dataset.columns
    : []

  setFileName(
    dataset.fileName ||
    (dataset.dataset_path
      ? dataset.dataset_path.split(/[\\/]/).pop()
      : 'pricing_data.csv')
  )

  setColumns(dataColumns)
  setRows(dataRows.slice(0, 5))
  setRowCount(
    dataset.rowCount ??
    (typeof dataset.rows === 'number'
      ? dataset.rows
      : dataRows.length)
  )

  const missing = {}
  const stats = {}

  dataColumns.forEach(column => {
    const values = dataRows.map(row =>
      String(row[column] ?? '').trim()
    )

    missing[column] = values.filter(
      value => value === ''
    ).length

    const numericValues = values
      .filter(value => value !== '')
      .map(Number)

    const allNumeric =
      numericValues.length > 0 &&
      values.every(
        value =>
          value === '' ||
          Number.isFinite(Number(value))
      )

    if (allNumeric) {
      stats[column] = {
        min: Math.min(...numericValues),
        max: Math.max(...numericValues),
        average:
          numericValues.reduce(
            (total, value) => total + value,
            0
          ) / numericValues.length
      }
    }
  })

  setMissingValues(missing)
  setStatistics(stats)
}, [dataset])


  function handleFileChange (event) {
    const file = event.target.files[0]

    setError('')
    setFileName('')
    setColumns([])
    setRows([])
    setMissingValues({})
    setStatistics({})
    setRowCount(0)

    if (!file) return

    if (!file.name.toLowerCase().endsWith('.csv')) {
      setError('Please select a CSV file.')
      return
    }

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      transformHeader: (() => {
        const seen = new Set()
        let duplicateFound = false

        const transform = header => {
          const cleaned = header.trim()

          if (seen.has(cleaned.toLowerCase())) {
            duplicateFound = true
          }

          seen.add(cleaned.toLowerCase())
          return cleaned
        }

        transform.hasDuplicates = () => duplicateFound
        return transform
      })(),

      complete: result => {
        if (result.meta.renamedHeaders) {
          setError('Duplicate column names were found. Please rename them.')
          return
        }
        const data = result.data
        const headers = result.meta.fields || []

        if (result.errors.length > 0) {
          setError('Some CSV rows could not be parsed. Please check your file.')
          return
        }

        if (headers.length === 0 || data.length === 0) {
          setError('The CSV must contain column headings and data rows.')
          return
        }

        if (headers.some(header => !header)) {
          setError('Every column must have a heading.')
          return
        }

        if (new Set(headers).size !== headers.length) {
          setError('Duplicate column names were found. Please rename them.')
          return
        }

        const missing = {}
        const stats = {}

        headers.forEach(column => {
          const values = data.map(row => String(row[column] ?? '').trim())

          missing[column] = values.filter(value => value === '').length

          const numericValues = values.filter(value => value !== '').map(Number)

          const allNumeric =
            numericValues.length > 0 &&
            values.every(
              value => value === '' || Number.isFinite(Number(value))
            )

          if (allNumeric) {
            const sorted = [...numericValues].sort((a, b) => a - b)
            const sum = numericValues.reduce((total, n) => total + n, 0)

            stats[column] = {
              min: Math.min(...numericValues),
              max: Math.max(...numericValues),
              average: sum / numericValues.length
            }
          }
        })

        setFileName(file.name)
        setColumns(headers)
        setRows(data.slice(0, 5))
        setRowCount(data.length)
        setMissingValues(missing)
        setStatistics(stats)

        if (onDatasetLoaded) {
          onDatasetLoaded({
            fileName: file.name,
            rowCount: data.length,
            columns: headers,
            rows: data
          })
        }
      },

      error: () => {
        setError('Unable to read the CSV file.')
      }
    })
  }

  const totalMissing = Object.values(missingValues).reduce(
    (total, count) => total + count,
    0
  )

  const hasPrice = columns.some(column => column.toLowerCase() === 'price')

  const hasSales = columns.some(column => column.toLowerCase() === 'sales')

  return (
    <section className='panel'>
      <h2>Upload Pricing Dataset</h2>
      <p>Upload your CSV to inspect its structure and data quality.</p>

      <input type='file' onChange={handleFileChange} />

      {error && (
        <p role='alert' style={{ color: '#c62828' }}>
          {error}
        </p>
      )}

      {fileName && !error && (
        <>
          <p>
            <strong>Selected file:</strong> {fileName}
          </p>

          <div className='stats-grid'>
            <div className='stat-card'>
              <p>Total Rows</p>
              <h2>{rowCount}</h2>
            </div>

            <div className='stat-card'>
              <p>Total Columns</p>
              <h2>{columns.length}</h2>
            </div>

            <div className='stat-card'>
              <p>Missing Cells</p>
              <h2>{totalMissing}</h2>
            </div>
          </div>

          <div className='panel'>
            <h3>Required Column Check</h3>
            <p>
              {hasPrice ? '✓' : '✗'} Price column{' '}
              {hasPrice ? 'found' : 'missing'}
            </p>
            <p>
              {hasSales ? '✓' : '✗'} Sales column{' '}
              {hasSales ? 'found' : 'missing'}
            </p>

            <p>
              {hasPrice && hasSales
                ? 'Basic column check passed. Further model-specific validation is still needed.'
                : 'Please check the column names before model integration.'}
            </p>
          </div>

          <div className='panel'>
            <h3>Missing Values by Column</h3>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={cellStyle}>Column</th>
                    <th style={cellStyle}>Missing Values</th>
                  </tr>
                </thead>
                <tbody>
                  {columns.map(column => (
                    <tr key={column}>
                      <td style={cellStyle}>{column}</td>
                      <td style={cellStyle}>{missingValues[column]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className='panel'>
            <h3>Numeric Statistics</h3>

            {Object.keys(statistics).length === 0 ? (
              <p>No numeric columns detected.</p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr>
                      <th style={cellStyle}>Column</th>
                      <th style={cellStyle}>Minimum</th>
                      <th style={cellStyle}>Maximum</th>
                      <th style={cellStyle}>Average</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(statistics).map(([column, stat]) => (
                      <tr key={column}>
                        <td style={cellStyle}>{column}</td>
                        <td style={cellStyle}>{stat.min.toFixed(2)}</td>
                        <td style={cellStyle}>{stat.max.toFixed(2)}</td>
                        <td style={cellStyle}>{stat.average.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className='panel'>
            <h3>Dataset Preview</h3>
            <p>
              Showing the first {rows.length} of {rowCount} rows.
            </p>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    {columns.map(column => (
                      <th key={column} style={cellStyle}>
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, index) => (
                    <tr key={index}>
                      {columns.map(column => (
                        <td key={column} style={cellStyle}>
                          {row[column] ?? ''}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </section>
  )
}

const cellStyle = {
  padding: '10px',
  textAlign: 'left',
  border: '1px solid #dbe3ef'
}
