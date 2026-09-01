import { useState } from 'react'
import Logo from './Logo'
import NavBar from './NavBar'
import { useAuth } from '../context/AuthContext'
import { useAppData } from '../context/AppDataContext'

const ROLE_LABEL = { waiter: 'Waiter', kitchen: 'Kitchen', admin: 'Admin' }

export default function TopBar({ active, onNavigate }) {
  const { user, logout } = useAuth()
  const { queue } = useAppData()

  const badgeText =
    user?.role === 'waiter'
      ? `${user.username} · Tables ${(user.tables || []).join(', ')}`
      : `${ROLE_LABEL[user?.role]} · ${user?.username}`

  return (
    <header className="topbar">
      <Logo onClick={() => onNavigate(NAV_LANDING[user?.role] || 'menu')} />
      <NavBar role={user?.role} active={active} onNavigate={onNavigate} queueCount={queue.length} />
      <div className="right-controls">
        <div className="waiter-badge clickable" onClick={() => onNavigate('profile')}>
          <span className="dot" />
          <span className="badge-text">{badgeText}</span>
        </div>
        <button className="logout-btn" onClick={logout}>
          Logout
        </button>
      </div>
    </header>
  )
}

const NAV_LANDING = { waiter: 'menu', kitchen: 'kitchen', admin: 'receipts' }
