import { useState, useEffect } from 'react'
import { useAppData } from '../../context/AppDataContext'
import { useAuth } from '../../context/AuthContext'
import { useToast } from '../../context/ToastContext'
import { SIDES } from '../../data/menu'
import Modal from '../../components/Modal'

const PAY_METHODS = ['Chapa', 'CBE', 'BOA', 'Telebirr', 'Awash', 'Cash']

export default function CustomerMenuPage({ onNavigate }) {
  const { user } = useAuth()
  const { customerPlaceOrder, fetchCustomerOrders, chapaPay, menuItems, fetchMenu } = useAppData()
  const { showToast } = useToast()

  const [orderModal, setOrderModal] = useState(null)
  const [successModal, setSuccessModal] = useState(null)
  const [placing, setPlacing] = useState(false)
  const [activeOrders, setActiveOrders] = useState([])

  const foods = menuItems.filter((i) => i.type === 'food')
  const drinks = menuItems.filter((i) => i.type === 'drink')

  useEffect(() => {
    if (menuItems.length === 0) fetchMenu()
  }, [menuItems.length, fetchMenu])

  useEffect(() => {
    if (!user) return
    let active = true
    const poll = () => {
      fetchCustomerOrders().then((orders) => {
        if (!active) return
        setActiveOrders(orders.filter((o) => o.status !== 'served' && o.status !== 'declined'))
      }).catch(() => {})
    }
    poll()
    const timer = setInterval(poll, 10000)
    return () => { active = false; clearInterval(timer) }
  }, [user, fetchCustomerOrders])

  const openOrder = (item) => {
    setOrderModal({ item, side: null, qty: 1, payment: null, error: '' })
  }

  const total = orderModal ? orderModal.item.price * orderModal.qty : 0
  const orderReady = orderModal && orderModal.side && orderModal.qty > 0 && orderModal.payment

  const confirmOrder = async () => {
    if (!orderModal) return
    setOrderModal((m) => ({ ...m, error: '' }))
    setPlacing(true)
    try {
      const result = await customerPlaceOrder(user.username, orderModal.item, {
        side: orderModal.side,
        qty: orderModal.qty,
        payment: orderModal.payment,
      })
      if (orderModal.payment === 'Chapa') {
        const chapaResult = await chapaPay(user.username, result.orderId, {
          email: user.email || '',
          phone: user.phone || '',
          amount: total,
        })
        if (chapaResult.success) {
          setPlacing(false)
          setOrderModal(null)
          setSuccessModal({
            orderId: result.orderId,
            total: result.total,
            payment: 'Chapa',
            txRef: chapaResult.txRef,
            time: result.time,
          })
          showToast('Payment successful!', 'success')
          return
        }
      }
      setPlacing(false)
      setOrderModal(null)
      setSuccessModal({
        orderId: result.orderId,
        total: result.total,
        payment: orderModal.payment,
        time: result.time,
      })
      showToast('Order placed!', 'success')
    } catch (err) {
      setOrderModal((m) => ({ ...m, error: err.message }))
    }
    setPlacing(false)
  }

  return (
    <div className="cust-menu-page">
      {activeOrders.length > 0 && (
        <div className="cust-pending-bar" onClick={() => onNavigate('tracking')}>
          <div className="cust-pending-pulse" />
          <span className="cust-pending-text">
            {activeOrders.length} order{activeOrders.length > 1 ? 's' : ''} pending
          </span>
          <span className="cust-pending-status">
            {activeOrders.some((o) => o.status === 'ready') ? 'Ready!' :
             activeOrders.some((o) => o.status === 'accepted') ? 'Accepted' : 'Pending...'}
          </span>
          <span className="cust-pending-arrow">→</span>
        </div>
      )}

      <div className="panel-title">Foods</div>
      <div className="menu-grid">
        {foods.map((item) => (
          <div key={item.id} className="item-card" onClick={() => openOrder(item)}>
            <div className="item-head">
              <span className="item-emoji">{item.emoji}</span>
              <span className="item-name">{item.name}</span>
            </div>
            <div className="item-price">{item.price} birr</div>
            <button
              className="accept-btn"
              onClick={(e) => { e.stopPropagation(); openOrder(item); }}
            >
              Order
            </button>
          </div>
        ))}
      </div>

      <div className="panel-title" style={{ marginTop: 20 }}>Drinks</div>
      <div className="menu-grid">
        {drinks.map((item) => (
          <div key={item.id} className="item-card" onClick={() => openOrder(item)}>
            <div className="item-head">
              <span className="item-emoji">{item.emoji}</span>
              <span className="item-name">{item.name}</span>
            </div>
            <div className="item-price">{item.price} birr</div>
            <button
              className="accept-btn"
              onClick={(e) => { e.stopPropagation(); openOrder(item); }}
            >
              Order
            </button>
          </div>
        ))}
      </div>

      <OrderModal data={orderModal} total={total} ready={orderReady} placing={placing}
        onClose={() => setOrderModal(null)} onUpdate={(p) => setOrderModal((m) => ({ ...m, ...p }))}
        onConfirm={confirmOrder} />
      <SuccessModal data={successModal} onClose={() => setSuccessModal(null)}
        onViewOrders={() => { setSuccessModal(null); onNavigate('tracking'); }} />
    </div>
  )
}

function OrderModal({ data, total, ready, placing, onClose, onUpdate, onConfirm }) {
  if (!data) return null
  const { item, side, qty, payment, error } = data

  return (
    <Modal open={!!data} onClose={onClose} title={item?.name?.toUpperCase()} subtitle={`${item?.price} birr each`}>
      <div className="cust-modal-emoji">{item?.emoji}</div>

      <div className="modal-section-label">Serve with</div>
      <div className="grid-3">
        {SIDES.map((s) => (
          <div key={s} className={`pick-box ${side === s ? 'selected' : ''}`} onClick={() => onUpdate({ side: s })}>
            {s}
          </div>
        ))}
      </div>

      <div className="modal-section-label">Quantity</div>
      <div className="grid-4">
        {[1, 2, 3, 4, 5, 6].map((q) => (
          <div key={q} className={`pick-box ${qty === q ? 'selected' : ''}`} onClick={() => onUpdate({ qty: q })}>
            {q}
          </div>
        ))}
      </div>

      <div className="cust-price-calc">
        <span>{item?.price} birr × {qty}</span>
        <span className="cust-price-total">{total} birr</span>
      </div>

      <div className="modal-section-label">Payment</div>
      <div className="grid-3">
        {PAY_METHODS.map((m) => (
          <div key={m} className={`pick-box pay-method ${payment === m ? 'selected' : ''}`} onClick={() => onUpdate({ payment: m })}>
            {m}
          </div>
        ))}
      </div>

      {error && <div className="form-error">{error}</div>}
      <button className="modal-primary-btn" disabled={!ready || placing} onClick={onConfirm}>
        {placing ? 'Processing...' :
         !side ? 'Select a side dish' :
         !payment ? 'Select payment method' :
         `Pay ${total} birr`}
      </button>
    </Modal>
  )
}

function SuccessModal({ data, onClose, onViewOrders }) {
  if (!data) return null
  return (
    <Modal open={!!data} onClose={onClose} title="ORDER PLACED" subtitle="Payment received">
      <div className="cust-success-icon">✓</div>
      <div className="cust-success-msg">Successfully Paid!</div>
      <div className="cust-success-tx">via {data.payment}{data.txRef ? ` (${data.txRef})` : ''}</div>
      <div className="cust-success-details">
        <div className="cust-success-row"><span>Order ID</span><span className="cust-success-id">{data.orderId}</span></div>
        <div className="cust-success-row"><span>Total</span><span>{data.total} birr</span></div>
        <div className="cust-success-row"><span>Time</span><span>{data.time}</span></div>
        <div className="cust-success-row"><span>Status</span><span className="cust-status-badge pending">Pending</span></div>
      </div>
      <div className="cust-success-note">
        Your order is in the queue. The waiter will accept it shortly.
      </div>
      <button className="modal-primary-btn" onClick={onViewOrders}>View My Orders</button>
    </Modal>
  )
}
