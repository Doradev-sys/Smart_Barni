export const NAV_CONFIG = {
  waiter: [
    { id: 'menu', label: 'Menu', icon: '🍽️' },
    { id: 'online', label: 'Online', icon: '🌐' },
    { id: 'reports', label: 'Reports', icon: '📊' },
    { id: 'history', label: 'History', icon: '📅' },
  ],
  kitchen: [
    { id: 'kitchen', label: 'Orders', icon: '👨‍🍳' },
    { id: 'reports', label: 'Reports', icon: '📋' },
    { id: 'history', label: 'History', icon: '📅' },
  ],
  admin: [
    { id: 'receipts', label: 'Receipts', icon: '🧾' },
    { id: 'reports', label: 'Reports', icon: '📈' },
    { id: 'history', label: 'History', icon: '📅' },
  ],
}

export default function NavBar({ role, active, onNavigate, queueCount }) {
  const items = NAV_CONFIG[role] || []

  return (
    <nav className="navbar" aria-label="Primary">
      {items.map((item) => (
        <button
          key={item.id}
          className={`nav-item ${active === item.id ? 'active' : ''}`}
          onClick={() => onNavigate(item.id)}
        >
          <span className="nav-icon">{item.icon}</span>
          <span className="nav-label">{item.label}</span>
          {item.id === 'online' && queueCount > 0 && (
            <span className="nav-badge">{queueCount}</span>
          )}
        </button>
      ))}
    </nav>
  )
}
