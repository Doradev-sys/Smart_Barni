import { useState } from 'react'
import TopBar from './components/TopBar'
import CustomerTopBar from './components/CustomerTopBar'
import LoginPage from './pages/LoginPage'
import TableSelectPage from './pages/TableSelectPage'
import MenuPage from './pages/waiter/MenuPage'
import OnlinePage from './pages/waiter/OnlinePage'
import WaiterReportsPage from './pages/waiter/WaiterReportsPage'
import KitchenOrdersPage from './pages/kitchen/KitchenOrdersPage'
import KitchenReportsPage from './pages/kitchen/KitchenReportsPage'
import AdminReceiptsPage from './pages/admin/AdminReceiptsPage'
import AdminReportsPage from './pages/admin/AdminReportsPage'
import HistoryPage from './pages/HistoryPage'
import ProfilePage from './pages/ProfilePage'
import CustomerMenuPage from './pages/customer/CustomerMenuPage'
import CustomerTrackingPage from './pages/customer/CustomerTrackingPage'
import CustomerHistoryPage from './pages/customer/CustomerHistoryPage'
import { useAuth } from './context/AuthContext'

const LANDING = {
  waiter: 'menu',
  kitchen: 'kitchen',
  admin: 'receipts',
  customer: 'menu',
}

export default function App() {
  const { user } = useAuth()
  const [tab, setTab] = useState(null)

  if (!user) return <LoginPage />
  if (user.step === 'tables') return <TableSelectPage />

  if (user.role === 'customer') {
    const activeTab = tab || 'menu'
    return (
      <div className="app-screen show cust-app">
        <CustomerTopBar active={activeTab} onNavigate={setTab} />
        <main className="main-app">
          <div className={`page ${activeTab === 'menu' ? 'show' : ''}`}>
            <CustomerMenuPage onNavigate={setTab} />
          </div>
          <div className={`page ${activeTab === 'tracking' ? 'show' : ''}`}>
            <CustomerTrackingPage />
          </div>
          <div className={`page ${activeTab === 'history' ? 'show' : ''}`}>
            <CustomerHistoryPage />
          </div>
          <div className={`page ${activeTab === 'profile' ? 'show' : ''}`}>
            <ProfilePage onNavigate={setTab} />
          </div>
        </main>
      </div>
    )
  }

  const activeTab = tab || LANDING[user.role]
  const NAV_ITEMS = {
    waiter: ['menu', 'online', 'reports', 'history', 'profile'],
    kitchen: ['kitchen', 'reports', 'history', 'profile'],
    admin: ['receipts', 'reports', 'history', 'profile'],
  }
  const isAllowed = (NAV_ITEMS[user.role] || []).some((n) => n === activeTab)
  const current = isAllowed ? activeTab : LANDING[user.role]

  return (
    <div className="app-screen show">
      <TopBar active={current} onNavigate={setTab} />
      <main className="main-app">
        <div className={`page ${current === 'menu' ? 'show' : ''}`}>
          <MenuPage />
        </div>
        <div className={`page ${current === 'online' ? 'show' : ''}`}>
          <OnlinePage />
        </div>
        <div className={`page ${current === 'kitchen' ? 'show' : ''}`}>
          <KitchenOrdersPage />
        </div>
        <div className={`page ${current === 'reports' ? 'show' : ''}`}>
          {user.role === 'waiter' && <WaiterReportsPage />}
          {user.role === 'kitchen' && <KitchenReportsPage />}
          {user.role === 'admin' && <AdminReportsPage />}
        </div>
        <div className={`page ${current === 'receipts' ? 'show' : ''}`}>
          <AdminReceiptsPage />
        </div>
        <div className={`page ${current === 'history' ? 'show' : ''}`}>
          <HistoryPage />
        </div>
        <div className={`page ${current === 'profile' ? 'show' : ''}`}>
          <ProfilePage onNavigate={setTab} />
        </div>
      </main>
    </div>
  )
}
