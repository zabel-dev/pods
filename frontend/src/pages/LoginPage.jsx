import { useState } from 'react'
import { Link, useNavigate, useOutletContext } from 'react-router-dom'
import './AuthPage.css'

export default function LoginPage() {
  const navigate = useNavigate()
  const { setUser } = useOutletContext()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        setError(data.detail || (typeof data === 'string' ? data : 'Login failed'))
        return
      }
      const user = data.user || { email: data.email || email.trim() }
      setUser(user)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.message || 'Could not reach server')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="wrap auth-wrap">
      <div className="auth-card">
        <h1>Log in</h1>
        <p className="subtitle">Enter your email and password</p>
        <form className="form auth-form" onSubmit={handleSubmit}>
          <label htmlFor="login-email">Email</label>
          <input
            id="login-email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
          />
          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />
          {error && <p className="auth-error">{error}</p>}
          <div className="row">
            <button type="submit" disabled={loading}>
              {loading ? 'Logging in…' : 'Log in'}
            </button>
          </div>
        </form>
        <p className="auth-footer">
          Don't have an account? <Link to="/register">Sign up</Link>
        </p>
      </div>
    </div>
  )
}
