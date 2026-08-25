import { useState, useEffect } from 'react'
import { useAppData } from '../../context/AppDataContext'
import { useAuth } from '../../context/AuthContext'

const STATUS_ORDER = ['pending', 'accepted', 'ready', 'served']
const STATUS_LABELS = {
  pending: 'Order Pending',
  accepted: 'Order Accepted',
  ready: 'Ready to Serve',
  served: 'Served',
}
const STATUS_ICONS = {
  pending: '⏳',
  accepted: '✓',
  ready: '🟢',
  served: '🍽️',
}

export default function CustomerTrackingPage() {
  const { user } = useAuth()
  const { fetchCustomerOrders } = useAppData()
  const [orders, setOrders] = useState([])
  const [, setTick] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => setTick((t) => t + 1), 1500)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    if (!user) return
    let active = true
    const poll = () => {
      fetchCustomerOrders().then((o) => { if (active) setOrders(o) }).catch(() => {})
    }
    poll()
    const timer = setInterval(poll, 10000)
    return () => { active = false; clearInterval(timer) }
  }, [user, fetchCustomerOrders])

  return (
    <div className="cust-tracking-page">
      <div className="cust-section">
        <div className="cust-section-header">
          <span className="cust-section-title">Active Orders</span>
          {active.length > 0 && <span className="cust-count-badge">{active.length}</span>}
        </div>
        {active.length === 0 ? (
          <div className="cust-empty">
            <div className="cust-empty-icon">📋</div>
            <div className="cust-empty-text">No active orders</div>
            <div className="cust-empty-sub">Place an order from the menu to see it here</div>
          </div>
        ) : (
          <div className="cust-tracking-list">
            {active.map((order) => (
              <TrackingCard key={order.orderId} order={order} />
            ))}
          </div>
        )}
      </div>

      {served.length > 0 && (
        <div className="cust-section">
          <div className="cust-section-header">
            <span className="cust-section-title">Served</span>
          </div>
          <div className="cust-tracking-list">
            {served.map((order) => (
              <TrackingCard key={order.orderId} order={order} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function TrackingCard({ order }) {
  const statusIdx = STATUS_ORDER.indexOf(order.status)

  return (
    <div className={`cust-track-card status-${order.status}`}>
      <div className="cust-track-top">
        <div className="cust-track-item">
          <span className="cust-track-emoji">{order.emoji}</span>
          <div>
            <div className="cust-track-name">{order.name}</div>
            <div className="cust-track-meta">
              {order.side} · ×{order.qty} · {order.total} birr
            </div>
          </div>
        </div>
        <div className="cust-track-id">{order.orderId}</div>
      </div>

      <div className="cust-track-progress">
        {STATUS_ORDER.map((s, i) => (
          <div key={s} className={`cust-track-step ${i <= statusIdx ? 'done' : ''} ${i === statusIdx ? 'current' : ''}`}>
            <div className="cust-track-dot">{STATUS_ICONS[s]}</div>
            <div className="cust-track-step-label">{STATUS_LABELS[s]}</div>
            {i < STATUS_ORDER.length - 1 && <div className="cust-track-line" />}
          </div>
        ))}
      </div>

      <div className={`cust-status-badge ${order.status}`}>
        {STATUS_LABELS[order.status]}
      </div>
    </div>
  )
}
