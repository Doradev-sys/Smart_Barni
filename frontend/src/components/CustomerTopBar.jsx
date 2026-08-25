import Logo from './Logo'
import { useAuth } from '../context/AuthContext'

const CUSTOMER_NAV = [
  { id: 'menu', label: 'Menu', icon: '🍽️' },
  { id: 'tracking', label: 'My Orders', icon: '📦' },
  { id: 'history', label: 'History', icon: '📜' },
]

export default function CustomerTopBar({ active, onNavigate }) {
  const { user, logout } = useAuth()

  return (
    <header className="topbar">
      <Logo onClick={() => onNavigate('menu')} />
      <nav className="navbar cust-navbar" aria-label="Customer navigation">
        {CUSTOMER_NAV.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${active === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="right-controls">
        <div className="waiter-badge clickable" onClick={() => onNavigate('profile')}>
          <span className="dot" />
          <span className="badge-text">{user?.fullName || user?.username}</span>
        </div>
        <button className="logout-btn" onClick={logout}>
          Logout
        </button>
      </div>
    </header>
  )
}
