import { useState, useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import Header from './Header'
import './Layout.css'

const USER_KEY = 'yt_subtitles_user'

function loadUser() {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function saveUser(user) {
  if (user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  } else {
    localStorage.removeItem(USER_KEY)
  }
}

export default function Layout() {
  const [user, setUserState] = useState(loadUser)

  useEffect(() => {
    saveUser(user)
  }, [user])

  function setUser(value) {
    setUserState(value)
  }

  function handleLogout() {
    setUser(null)
  }

  return (
    <div className="layout">
      <Header user={user} onLogout={handleLogout} />
      <main className="layout-main">
        <Outlet context={{ user, setUser }} />
      </main>
    </div>
  )
}
