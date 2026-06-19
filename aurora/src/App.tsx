import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Editor from './pages/Editor'
import Present from './pages/Present'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/editor" element={<Editor />} />
      <Route path="/present" element={<Present />} />
    </Routes>
  )
}
