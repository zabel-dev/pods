import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import './VideoPage.css'

function parseError(text) {
  try {
    const j = JSON.parse(text)
    if (j.detail) return typeof j.detail === 'string' ? j.detail : j.detail.join?.(' ') || text
  } catch (_) {}
  return text
}

function getYoutubeVideoId(url) {
  if (!url) return null
  try {
    const u = new URL(url)
    if (u.hostname === 'youtu.be') return u.pathname.slice(1).split('?')[0] || null
    if (u.hostname === 'www.youtube.com' || u.hostname === 'youtube.com') return u.searchParams.get('v') || null
  } catch (_) {}
  return null
}

const TIMESTAMP_LINE = /^(\d{2}:\d{2}:\d{2}) - (\d{2}:\d{2}:\d{2}): (.+)$/

function timestampToSeconds(hhmmss) {
  const parts = (hhmmss || '').trim().split(':').map(Number)
  if (parts.length < 3) return 0
  return (parts[0] || 0) * 3600 + (parts[1] || 0) * 60 + (parts[2] || 0)
}

function parseTimestampLines(text) {
  if (!text || !text.trim()) return []
  return text.trim().split('\n').map((line) => {
    const m = line.match(TIMESTAMP_LINE)
    if (m) return { start: m[1], end: m[2], text: m[3], raw: line }
    return { raw: line }
  })
}

// Поддерживаем и обычный дефис -, и длинное тире – между таймкодами,
// чтобы парсить форматы вроде [00:00:01-00:00:10] и [00:00:01–00:00:10]
const GROK_TIMESTAMP_RE =
  /\[(\d{2}:\d{2}:\d{2})\s*[-–]\s*(\d{2}:\d{2}:\d{2})\]/g

function renderChatContent(content, seekTo) {
  if (!content) return null
  const parts = []
  let lastIndex = 0
  let match
  GROK_TIMESTAMP_RE.lastIndex = 0
  while ((match = GROK_TIMESTAMP_RE.exec(content)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', value: content.slice(lastIndex, match.index), key: `t-${lastIndex}` })
    }
    parts.push({ type: 'timestamp', start: match[1], end: match[2], key: `ts-${match.index}` })
    lastIndex = match.index + match[0].length
  }
  if (lastIndex < content.length) {
    parts.push({ type: 'text', value: content.slice(lastIndex), key: `t-${lastIndex}` })
  }
  if (parts.length === 0) return content
  return parts.map((p) =>
    p.type === 'text' ? (
      <span key={p.key}>{p.value}</span>
    ) : (
      <button
        key={p.key}
        type="button"
        className="chat-msg-timestamp"
        onClick={() => seekTo(timestampToSeconds(p.start))}
      >
        [{p.start}-{p.end}]
      </button>
    )
  )
}

export default function VideoPage() {
  const [searchParams] = useSearchParams()
  const urlFromQuery = searchParams.get('url') || ''

  const [loading, setLoading] = useState(false)
  const [showPlain, setShowPlain] = useState(true)
  const [plain, setPlain] = useState({ type: 'placeholder', text: 'Subtitle text will appear here.' })
  const [withTimestamps, setWithTimestamps] = useState({ type: 'placeholder', text: 'Subtitles with timestamps will appear here.' })
  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [videoInfo, setVideoInfo] = useState(null)
  const [copyFeedback, setCopyFeedback] = useState(false)
  const chatMessagesRef = useRef(null)
  const playerRef = useRef(null)
  const videoId = getYoutubeVideoId(decodeURIComponent(urlFromQuery || ''))

  useEffect(() => {
    if (!urlFromQuery) return
    const u = decodeURIComponent(urlFromQuery)
    const ac = new AbortController()
    setVideoInfo(null)
    setPlain({ type: 'placeholder', text: 'Loading…' })
    setWithTimestamps({ type: 'placeholder', text: 'Loading…' })
    setLoading(true)
    ;(async () => {
      try {
        const infoRes = await fetch('/api/video/video-info', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ source_url: u }),
          signal: ac.signal,
        })
        const infoData = await infoRes.json().catch(() => ({}))
        if (!infoRes.ok) throw infoData
        setVideoInfo(infoData)

        const subsRes = await fetch('/api/video/subtitles', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ source_url: u }),
          signal: ac.signal,
        })
        const subsData = await subsRes.json().catch(() => ({}))
        if (!subsRes.ok) throw subsData

        setPlain({ type: 'success', text: subsData.subtitles || 'No subtitles found.' })
        setWithTimestamps({ type: 'success', text: subsData.subtitles_ts || 'No subtitles found.' })
      } catch (err) {
        if (err?.name === 'AbortError') return
        setVideoInfo(null)
        const msg = Array.isArray(err?.detail)
          ? err.detail.join(' ')
          : (err?.detail || parseError(JSON.stringify(err)))
        setPlain({ type: 'error', text: msg })
        setWithTimestamps({ type: 'placeholder', text: '—' })
      } finally {
        setLoading(false)
      }
    })()
    return () => ac.abort()
  }, [urlFromQuery])

  const active = showPlain ? plain : withTimestamps
  const showChat = plain.type === 'success' && plain.text
  const canSend = showChat && !chatLoading

  useEffect(() => {
    const el = chatMessagesRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [chatMessages, chatLoading])

  useEffect(() => {
    if (!videoId) return
    function initPlayer() {
      if (!window.YT || !window.YT.Player) return
      const el = document.getElementById('yt-player')
      if (!el) return
      playerRef.current = new window.YT.Player('yt-player', {
        events: { onReady: (e) => { playerRef.current = e.target } }
      })
    }
    if (window.YT && window.YT.Player) {
      initPlayer()
      return
    }
    window.onYouTubeIframeAPIReady = initPlayer
    if (!document.getElementById('youtube-iframe-api')) {
      const s = document.createElement('script')
      s.id = 'youtube-iframe-api'
      s.src = 'https://www.youtube.com/iframe_api'
      document.head.appendChild(s)
    }
    return () => { window.onYouTubeIframeAPIReady = null }
  }, [videoId])

  function seekTo(seconds) {
    try {
      const s = Math.max(0, Math.floor(seconds || 0))
      if (playerRef.current && typeof playerRef.current.seekTo === 'function') {
        playerRef.current.seekTo(s, true)
        return
      }
    } catch (_) {}
    // Fallback: if the YouTube Iframe API is not available (e.g. file:// or blocked),
    // try to jump by updating the iframe URL with a start time.
    try {
      const iframe = document.getElementById('yt-player')
      if (iframe && iframe.tagName === 'IFRAME') {
        const url = new URL(iframe.src, window.location.href)
        const s = Math.max(0, Math.floor(seconds || 0))
        url.searchParams.set('start', String(s))
        url.searchParams.set('t', String(s))
        url.searchParams.set('enablejsapi', '1')
        iframe.src = url.toString()
      }
    } catch (_) {}
  }

  async function copyResult() {
    const text = active.type === 'success' && active.text ? active.text : ''
    if (!text) return
    try {
      await navigator.clipboard.writeText(text)
      setCopyFeedback(true)
      setTimeout(() => setCopyFeedback(false), 2000)
    } catch (_) {}
  }

  async function handleChatSubmit(e) {
    e.preventDefault()
    const msg = chatInput.trim()
    if (!msg || !canSend) return
    const userMsg = { role: 'user', content: msg }
    setChatMessages((prev) => [...prev, userMsg])
    setChatInput('')
    setChatLoading(true)
    try {
      const res = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subtitles_text: (withTimestamps.type === 'success' && withTimestamps.text) ? withTimestamps.text : plain.text,
          messages: [...chatMessages, userMsg],
        }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        setChatMessages((prev) => [...prev, { role: 'assistant', content: 'Error: ' + (data.detail || res.statusText) }])
        return
      }
      setChatMessages((prev) => [...prev, { role: 'assistant', content: data.content || '—' }])
    } catch (err) {
      setChatMessages((prev) => [...prev, { role: 'assistant', content: 'Error: ' + (err.message || 'cannot reach server') }])
    } finally {
      setChatLoading(false)
    }
  }

  if (!urlFromQuery) {
    return (
      <div className="wrap">
        <div className="summary-actions">
          <Link to="/" className="back-btn">← Back to list</Link>
        </div>
        <h1>YouTube Subtitles</h1>
        <p className="subtitle">No video selected. <Link to="/">Choose a video from the list</Link> or add a new link on the main page.</p>
        <footer className="footer">YouTube Subtitles</footer>
      </div>
    )
  }

  return (
    <div className="wrap">
      <div className="summary-actions">
        <Link to="/" className="back-btn">← Back to list</Link>
      </div>

      {videoId && (
        <div className="video-embed">
          <iframe
            id="yt-player"
            title="YouTube video"
            src={`https://www.youtube.com/embed/${videoId}?enablejsapi=1`}
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowFullScreen
            className="video-embed-iframe"
          />
          {videoInfo?.title && <div className="video-embed-title">{videoInfo.title}</div>}
        </div>
      )}

      {showChat && (
        <div className="chat-section">
          <h2 className="chat-title">Chat with Grok</h2>
          <div className="chat-messages" ref={chatMessagesRef}>
            {chatMessages.length === 0 && (
              <div className="chat-placeholder">Ask Grok to summarize the subtitles or ask anything about the video.</div>
            )}
            {chatMessages.map((m, i) => (
              <div key={i} className={`chat-msg chat-msg--${m.role}`}>
                <div className="chat-msg-content">{renderChatContent(m.content, seekTo)}</div>
              </div>
            ))}
            {chatLoading && (
              <div className="chat-msg chat-msg--assistant chat-msg--typing">
                <div className="chat-msg-content chat-typing">
                  <span className="chat-typing-dot" />
                  <span className="chat-typing-dot" />
                  <span className="chat-typing-dot" />
                </div>
              </div>
            )}
          </div>
          <form className="chat-form" onSubmit={handleChatSubmit}>
            <input
              type="text"
              className="chat-input"
              placeholder="Type a message…"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              disabled={chatLoading}
            />
            <button type="submit" className="chat-send" disabled={!canSend || !chatInput.trim()}>
              Send
            </button>
          </form>
        </div>
      )}

      <div className="result-section">
        {loading ? (
          <div className="result result--loading">
            <div className="subtitle-loading">
              <div className="subtitle-loading-spinner" aria-hidden />
              <p className="subtitle-loading-text">Generating subtitles…</p>
              <p className="subtitle-loading-hint">Fetching from YouTube, please wait</p>
            </div>
          </div>
        ) : (
          <>
            <div className="result-actions">
              <div className="result-toggle">
                <button
                  type="button"
                  className={showPlain ? 'active' : ''}
                  onClick={() => setShowPlain(true)}
                >
                  Plain text
                </button>
                <button
                  type="button"
                  className={!showPlain ? 'active' : ''}
                  onClick={() => setShowPlain(false)}
                >
                  With timestamps
                </button>
              </div>
            </div>
            <div className={`result ${active.type}`} aria-live="polite">
              {!showPlain && withTimestamps.type === 'success' && withTimestamps.text ? (
                parseTimestampLines(withTimestamps.text).map((row, i) => (
                  row.start != null ? (
                    <div key={i} className="subtitle-line">
                      <button
                        type="button"
                        className="subtitle-timestamp"
                        onClick={() => seekTo(timestampToSeconds(row.start))}
                      >
                        {row.start}
                      </button>
                      <span className="subtitle-line-text"> – {row.end}: {row.text}</span>
                    </div>
                  ) : (
                    <div key={i} className="subtitle-line">{row.raw}</div>
                  )
                ))
              ) : (
                active.text
              )}
            </div>
            <button
              type="button"
              className="result-copy-btn"
              onClick={copyResult}
              disabled={active.type !== 'success' || !active.text}
              title="Copy current subtitles to clipboard"
            >
              <span className="result-copy-text">
                {copyFeedback ? 'Copied' : 'Copy subtitles'}
              </span>
              <span className="result-copy-icon" aria-hidden="true">📋</span>
            </button>
          </>
        )}
      </div>

      <footer className="footer">
        YouTube Subtitles
      </footer>
    </div>
  )
}
