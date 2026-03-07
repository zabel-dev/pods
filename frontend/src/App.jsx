import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HistoryPage from './pages/HistoryPage'
import VideoPage from './pages/VideoPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import './App.css'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HistoryPage />} />
        <Route path="/video" element={<VideoPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>
    </Routes>
  )
}
