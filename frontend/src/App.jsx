import { Routes, Route } from 'react-router-dom'
import HistoryPage from './pages/HistoryPage'
import VideoPage from './pages/VideoPage'
import './App.css'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HistoryPage />} />
      <Route path="/video" element={<VideoPage />} />
    </Routes>
  )
}
