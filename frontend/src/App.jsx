import { useMemo, useState } from 'react'

const fields = [
  'serialno', 'version', 'account-id', 'instance-id', 'srcaddr', 'dstaddr',
  'srcport', 'dstport', 'protocol', 'packets', 'bytes', 'starttime', 'endtime',
  'action', 'log-status'
]

const initialValues = Object.fromEntries(fields.map((field) => [field, '']))
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || ''

export default function App() {
  const [form, setForm] = useState(initialValues)
  const [results, setResults] = useState([])
  const [count, setCount] = useState(0)
  const [searchTime, setSearchTime] = useState(null)
  const [message, setMessage] = useState('Upload an archive to begin indexing the event data.')
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [searching, setSearching] = useState(false)

  const activeFilters = useMemo(
    () => Object.entries(form).filter(([, value]) => String(value).trim() !== ''),
    [form],
  )

  const handleFieldChange = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }))
  }

  const handleUpload = async () => {
    if (!file) {
      setMessage('Choose a .tgz or .gz archive before uploading.')
      return
    }

    const data = new FormData()
    data.append('file', file)
    setUploading(true)
    setMessage('Uploading archive and indexing records...')

    try {
      const response = await fetch(`${apiBaseUrl}/api/upload/`, { method: 'POST', body: data })
      const payload = await response.json()
      if (!response.ok) {
        throw new Error(payload.error || 'Upload failed')
      }
      setMessage(`Uploaded ${payload.records} records from ${payload.file}.`)
    } catch (error) {
      setMessage(error.message)
    } finally {
      setUploading(false)
    }
  }

  const handleSearch = async () => {
    const payload = Object.fromEntries(activeFilters)

    if (Object.keys(payload).length === 0) {
      setMessage('Enter at least one field value to search.')
      setResults([])
      setCount(0)
      setSearchTime(null)
      return
    }

    setSearching(true)
    setMessage('Searching indexed records...')

    try {
      const response = await fetch(`${apiBaseUrl}/api/search/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Search failed')
      }

      setResults(data.results || [])
      setCount(data.count || 0)
      setSearchTime(data.search_time)
      setMessage(data.results?.length ? `Found ${data.count} results.` : 'No matching events found.')
    } catch (error) {
      setMessage(error.message)
      setResults([])
      setCount(0)
      setSearchTime(null)
    } finally {
      setSearching(false)
    }
  }

  const resetFilters = () => {
    setForm(initialValues)
    setResults([])
    setCount(0)
    setSearchTime(null)
    setMessage('Filters cleared. Upload a new archive or search again.')
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">ACEABLE CYBER SOLUTIONS</p>
          <h1>Event Search Application</h1>
        </div>
        <p className="subtitle">Fast multi-field search across event log archives.</p>
      </header>

      <section className="panel upload-panel">
        <div className="panel-header">
          <h2>Upload Archive</h2>
        </div>
        <div className="upload-row">
          <label className="upload-input">
            <span>Archive (.tgz)</span>
            <input type="file" accept=".tgz,.tar.gz,.gz" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          </label>
          <button onClick={handleUpload} disabled={uploading || !file}>
            {uploading ? 'Uploading...' : 'Upload Archive'}
          </button>
        </div>
      </section>

      <section className="panel search-panel">
        <div className="panel-header">
          <h2>Search Filters</h2>
          <button className="secondary" onClick={resetFilters}>Clear</button>
        </div>

        <div className="field-grid">
          {fields.map((field) => (
            <label key={field} className="field">
              <span>{field}</span>
              <input
                value={form[field]}
                onChange={(e) => handleFieldChange(field, e.target.value)}
                placeholder={field}
              />
            </label>
          ))}
        </div>

        <div className="actions">
          <button onClick={handleSearch} disabled={searching}>
            {searching ? 'Searching...' : 'Search Events'}
          </button>
          <span className="filter-count">{activeFilters.length} active filters</span>
        </div>

        {message && <div className="message">{message}</div>}
      </section>

      <section className="panel results-panel">
        <div className="panel-header">
          <h2>Results</h2>
          {searchTime !== null && <span className="summary">{count} matches • {searchTime} sec</span>}
        </div>

        {results.length === 0 ? (
          <p className="empty-state">No results yet. Upload a log archive and search by one or more event fields.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  {fields.map((field) => <th key={field}>{field}</th>)}
                  <th>File</th>
                </tr>
              </thead>
              <tbody>
                {results.map((row, index) => (
                  <tr key={`${row.file}-${index}`}>
                    {fields.map((field) => <td key={`${field}-${index}`}>{row[field] ?? ''}</td>)}
                    <td>{row.file}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}
