import { useEffect, useState } from 'react'
import SubClaimCard from './components/SubClaimCard'
import './App.css'

function App() {
  const [text, setText] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [pastStances, setPastStances] = useState<any[]>([])

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/stances`)
      .then((res) => res.json())
      .then(setPastStances)
      .catch(() => {})
  }, [result])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    const formData = new FormData()
    formData.append('text', text)
    if (file) {
      formData.append('file', file)
    }

    let res: Response
    try {
      res = await fetch(`${import.meta.env.VITE_API_URL}/stances/upload`, {
        method: 'POST',
        body: formData,
      })
    } catch (err) {
      setError('Could not reach the server. Is the backend running?')
      setLoading(false)
      return
    }

    if (res.status === 429) {
      setError("You've hit the submission limit. Try again in a bit.")
    } else if (res.status === 422) {
      setError('Stance must be between 5 and 500 characters.')
    } else if (!res.ok) {
      setError('Something went wrong.')
    } else {
      const data = await res.json()
      setResult(data)
      setFile(null)
    }

    setLoading(false)
  }

  async function viewStance(id: number) {
    setError('')
    const res = await fetch(`${import.meta.env.VITE_API_URL}/stances/${id}`)
    const data = await res.json()
    setResult(data)
  }

  return (
    <div className="page">
      <h1>Stance Validator</h1>
      <form className="stance-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter a stance you hold..."
          minLength={5}
          maxLength={500}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Working...' : 'Submit'}
        </button>
      </form>

      <div className="file-attach">
        <label htmlFor="source-upload">Upload your own source to use (optional, PDF)</label>
        <input
          id="source-upload"
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        {file && (
          <span className="file-name">
            {file.name}{' '}
            <button type="button" className="link-button" onClick={() => setFile(null)}>
              ✕
            </button>
          </span>
        )}
      </div>

      {error && <p className="error">{error}</p>}

      {result && result.status === 'out_of_scope' && (
        <div className="digest">
          <h2>{result.text}</h2>
          <p className="out-of-scope">{result.out_of_scope_reason}</p>
        </div>
      )}

      {result && result.status !== 'out_of_scope' && (
        <div className="digest">
          <h2>{result.text}</h2>
          {result.topic_name && <p className="topic-name">Topic: {result.topic_name}</p>}
          <p className={`overall overall-${result.overall_lean}`}>
            {result.overall_lean.replaceAll('_', ' ')}
          </p>

          {result.sub_claims.map((sc: any, i: number) => (
            <SubClaimCard key={i} subClaim={sc} />
          ))}
        </div>
      )}

      {pastStances.length > 0 && (
        <div className="past-stances">
          <h2>Past stances</h2>
          <ul>
            {pastStances.map((s: any) => (
              <li key={s.id}>
                <button className="link-button" onClick={() => viewStance(s.id)}>
                  {s.text}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default App
