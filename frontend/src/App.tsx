import { useState } from 'react'
import SubClaimCard from './components/SubClaimCard'
import './App.css'

function App() {
  const [text, setText] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/stances`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })

      if (!res.ok) {
        throw new Error('Something went wrong.')
      }

      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError('Could not reach the server. Is the backend running?')
    } finally {
      setLoading(false)
    }
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
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Working...' : 'Submit'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="digest">
          <h2>{result.text}</h2>
          <p className={`overall overall-${result.overall_lean}`}>
            {result.overall_lean.replaceAll('_', ' ')}
          </p>

          {result.sub_claims.map((sc: any, i: number) => (
            <SubClaimCard key={i} subClaim={sc} />
          ))}
        </div>
      )}
    </div>
  )
}

export default App
