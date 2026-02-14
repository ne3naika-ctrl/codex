import { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

export default function App() {
  const [text, setText] = useState('')
  const [sourceName, setSourceName] = useState('manual_input')
  const [file, setFile] = useState(null)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [message, setMessage] = useState('')

  const uploadText = async () => {
    setMessage('')
    const response = await fetch(`${API_BASE}/ingest/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_name: sourceName, text }),
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.detail || 'Ошибка загрузки текста')
    setMessage(`Сохранено чанков: ${data.chunks}`)
  }

  const uploadFile = async () => {
    if (!file) throw new Error('Выберите файл .md или .pdf')
    setMessage('')
    const formData = new FormData()
    formData.append('file', file)
    const response = await fetch(`${API_BASE}/ingest/file`, {
      method: 'POST',
      body: formData,
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.detail || 'Ошибка загрузки файла')
    setMessage(`Сохранено чанков: ${data.chunks}`)
  }

  const runSearch = async () => {
    const response = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, limit: 5 }),
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.detail || 'Ошибка поиска')
    setResults(data.results ?? [])
  }

  const onAction = (fn) => async (event) => {
    event.preventDefault()
    try {
      await fn()
    } catch (error) {
      setMessage(error.message)
    }
  }

  return (
    <main className="container">
      <h1>Local RAG Ingest UI</h1>

      <section className="card">
        <h2>Текст</h2>
        <input
          value={sourceName}
          onChange={(e) => setSourceName(e.target.value)}
          placeholder="Имя источника"
        />
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Вставьте текст для сохранения в pgvector"
          rows={8}
        />
        <button onClick={onAction(uploadText)}>Сохранить текст</button>
      </section>

      <section className="card">
        <h2>Файл (.md / .pdf)</h2>
        <input
          type="file"
          accept=".md,.pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        <button onClick={onAction(uploadFile)}>Сохранить файл</button>
      </section>

      <section className="card">
        <h2>Проверка поиска</h2>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Введите вопрос"
        />
        <button onClick={onAction(runSearch)}>Поиск</button>
        <ul>
          {results.map((item, idx) => (
            <li key={idx}>
              <strong>{item.source_name}</strong> ({item.source_type}) — score: {item.score.toFixed(3)}
              <p>{item.content}</p>
            </li>
          ))}
        </ul>
      </section>

      {message && <p className="message">{message}</p>}
    </main>
  )
}
