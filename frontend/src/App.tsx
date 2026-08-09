import { useState } from 'react'
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
      const res = await fetch('http://localhost:8000/stances', {
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
    <div>
      <h1>Stance Validator</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter a stance you hold..."
        />
        <button type="submit">Submit</button>
      </form>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {result && (
        <div>
          <h2>{result.text}</h2>
          {result.sub_claims.map((sc: any, i: number) => (
            <div key={i}>
              <h3>{sc.text}</h3>
              <p>Strength: {sc.strength}</p>
              <ul>
                {sc.evidence.map((e: any, j: number) => (
                  <li key={j}>
                    <strong>{e.relation}</strong>: {e.summary} (
                    <a href={e.url}>{e.url}</a>)
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App
