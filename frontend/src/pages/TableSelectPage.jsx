import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { ALL_TABLES } from '../data/menu'

export default function TableSelectPage() {
  const { user, startShift } = useAuth()
  const [selected, setSelected] = useState([])

  const toggle = (t) =>
    setSelected((s) => (s.includes(t) ? s.filter((x) => x !== t) : [...s, t]))

  return (
    <div className="app-screen center-screen show">
      <div className="login-card" style={{ maxWidth: 460 }}>
        <div className="login-title" style={{ textAlign: 'center', width: '100%' }}>
          SELECT YOUR TABLES
        </div>
        <div className="login-tagline" style={{ textAlign: 'center', display: 'block' }}>
          Choose as many as you'll be serving this shift
        </div>
        <div className="table-select-grid">
          {ALL_TABLES.map((t) => (
            <div
              key={t}
              className={`table-box ${selected.includes(t) ? 'selected' : ''}`}
              onClick={() => toggle(t)}
            >
              {t}
            </div>
          ))}
        </div>
        <button
          className="modal-primary-btn"
          disabled={selected.length === 0}
          onClick={() => startShift([...selected].sort((a, b) => a - b))}
        >
          Start Shift →
        </button>
      </div>
    </div>
  )
}
