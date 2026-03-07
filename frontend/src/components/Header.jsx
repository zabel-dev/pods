import { Link } from 'react-router-dom'
import './Header.css'

export default function Header({ user, onLogout }) {
  return (
    <header className="app-header">
      <div className="app-header-inner wrap">
        <Link to="/" className="app-header-logo">
          SubtiMind AI
        </Link>
        <nav className="app-header-nav">
          {user ? (
            <>
              <span className="app-header-user">{user.email}</span>
              <button type="button" className="app-header-btn" onClick={onLogout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="app-header-link">
                Log in
              </Link>
              <Link to="/register" className="app-header-btn app-header-btn-primary">
                Sign up
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}
