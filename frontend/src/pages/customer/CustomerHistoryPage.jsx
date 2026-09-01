import { useState, useEffect } from 'react'
import { useAppData } from '../../context/AppDataContext'
import { useAuth } from '../../context/AuthContext'

export default function CustomerHistoryPage() {
  const { user } = useAuth()
  const { fetchCustomerOrders } = useAppData()
  const [orders, setOrders] = useState([])

  useEffect(() => {
    if (!user) return
    fetchCustomerOrders().then(setOrders).catch(() => {})
  }, [user, fetchCustomerOrders])

  const served = orders.filter((o) => o.status === 'served')
  const allDone = orders.filter((o) => o.status === 'served' || o.status === 'declined')

  const totalSpent = served.reduce((s, o) => s + o.total, 0)

  return (
    <div className="cust-history-page">
      <div className="cust-section">
        <div className="cust-section-header">
          <span className="cust-section-title">Order History</span>
        </div>

        <div className="cust-history-summary">
          <div className="cust-history-stat">
            <div className="cust-history-stat-label">Total Orders</div>
            <div className="cust-history-stat-value">{allDone.length}</div>
          </div>
          <div className="cust-history-stat">
            <div className="cust-history-stat-label">Total Spent</div>
            <div className="cust-history-stat-value">{totalSpent} birr</div>
          </div>
          <div className="cust-history-stat">
            <div className="cust-history-stat-label">Served</div>
            <div className="cust-history-stat-value">{served.length}</div>
          </div>
        </div>

        {allDone.length === 0 ? (
          <div className="cust-empty">
            <div className="cust-empty-icon">📜</div>
            <div className="cust-empty-text">No order history yet</div>
            <div className="cust-empty-sub">Your completed orders will appear here</div>
          </div>
        ) : (
          <div className="cust-history-list">
            {allDone.map((order) => (
              <HistoryCard key={order.orderId} order={order} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function HistoryCard({ order }) {
  return (
    <div className={`cust-history-card status-${order.status}`}>
      <div className="cust-history-top">
        <div className="cust-history-item">
          <span className="cust-history-emoji">{order.emoji}</span>
          <div>
            <div className="cust-history-name">{order.name}</div>
            <div className="cust-history-meta">
              {order.side} · ×{order.qty}
            </div>
          </div>
        </div>
        <div className="cust-history-right">
          <div className="cust-history-total">{order.total} birr</div>
          <div className={`cust-status-badge ${order.status}`}>
            {order.status === 'served' ? 'Served' : 'Declined'}
          </div>
        </div>
      </div>
      <div className="cust-history-bottom">
        <span className="cust-history-id">{order.orderId}</span>
        <span className="cust-history-time">{order.time}</span>
        <span className="cust-history-payment">{order.payment}</span>
      </div>
    </div>
  )
}
