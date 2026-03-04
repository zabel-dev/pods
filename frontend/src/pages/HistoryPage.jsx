import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import './HistoryPage.css'

export default function HistoryPage() {
  const navigate = useNavigate()
  const [list, setList] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [url, setUrl] = useState('https://www.youtube.com/watch?v=9fd5iBK6wsE')

  useEffect(() => {
    fetch('/api/youtube/history')
      .then((r) => (r.ok ? r.json() : Promise.reject(r)))
      .then(setList)
      .catch(() => setError('Failed to load history'))
      .finally(() => setLoading(false))
  }, [])

  function handleSubmit(e) {
    e.preventDefault()
    const trimmed = url.trim()
    if (!trimmed) return
    navigate(`/video?url=${encodeURIComponent(trimmed)}`)
  }

  return (
    <div className="wrap history-wrap">
      <header className="history-header">
        <h1>YouTube Subtitles</h1>
        <p className="subtitle">Add a video link to get subtitles, or pick one from history.</p>
        <form className="form add-video-form" onSubmit={handleSubmit}>
          <label htmlFor="url">Video link</label>
          <input
            type="url"
            id="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            required
            autoComplete="off"
          />
          <div className="row">
            <button type="submit">
              Get subtitles
            </button>
          </div>
        </form>
      </header>

      {loading && <p className="history-status">Loading…</p>}
      {error && <p className="history-status error">{error}</p>}

      {!loading && !error && list.length === 0 && (
        <p className="history-status empty">
          No videos in history yet. Add a link above to get started.
        </p>
      )}

      {!loading && !error && list.length > 0 && (
        <ul className="history-grid">
          {list.map((item, i) => (
            <li key={`${item.source_url}-${i}`}>
              <Link to={`/video?url=${encodeURIComponent(item.source_url)}`} className="history-card">
                <div className="history-card-thumb">
                  {item.thumbnail_url ? (
                    <img src={item.thumbnail_url} alt="" />
                  ) : (
                    <div className="history-card-thumb-placeholder">No preview</div>
                  )}
                </div>
                <div className="history-card-title">{item.title || 'Untitled'}</div>
              </Link>
            </li>
          ))}
        </ul>
      )}

      <footer className="footer">
        YouTube Subtitles
      </footer>
    </div>
  )
}
