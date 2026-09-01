import { useState, useEffect } from 'react'
import Modal from '../../components/Modal'
import Receipt from '../../components/Receipt'
import QRScanner from '../../components/QRScanner'
import { Panel, SectionLabel, EmptyHint } from '../../components/ui'
import { useAuth } from '../../context/AuthContext'
import { useAppData } from '../../context/AppDataContext'
import { useToast } from '../../context/ToastContext'
import { SIDES, PAY_METHODS } from '../../data/menu'

export default function MenuPage() {
  const { user } = useAuth()
  const { orders, placeOrder, cancelOrder, payOrder, menuItems, fetchMenu } = useAppData()
  const { showToast } = useToast()

  const [accept, setAccept] = useState(null)
  const [paying, setPaying] = useState(null)
  const [cancel, setCancel] = useState(null)
  const [receipt, setReceipt] = useState(null)
  const [qrOpen, setQrOpen] = useState(false)
  const [qrScanLog, setQrScanLog] = useState(null)

  const foods = menuItems.filter((i) => i.type === 'food')
  const drinks = menuItems.filter((i) => i.type === 'drink')

  useEffect(() => {
    if (menuItems.length === 0) fetchMenu()
  }, [menuItems.length, fetchMenu])

  const openAccept = (item) =>
    setAccept({ item, tables: user.tables, table: null, qty: null, side: null })
  const acceptReady = accept && accept.table && accept.qty && accept.side

  const confirmAccept = async () => {
    await placeOrder(accept.item, accept)
    showToast('Sent to kitchen 👨‍🍳', 'success')
    setAccept(null)
  }

  const openPay = (order) => setPaying({ order, method: null, qrData: null })

  const confirmPay = async () => {
    const receipt = await payOrder(paying.order, {
      waiter: user.username,
      method: paying.method,
      itemLabel:
        paying.order.source === 'online'
          ? paying.order.name
          : `${paying.order.name} (${paying.order.side})`,
      qrData: paying.qrData || null,
    })
    showToast('Payment recorded ✓', 'success')
    setPaying(null)
    setReceipt(receipt)
  }

  const handleQrScan = (data) => {
    setPaying((p) => p ? { ...p, qrData: data } : null)
    showToast('QR data captured ✓', 'success')
  }

  const serveOnline = async (order) => {
    const receipt = await payOrder(order, {
      waiter: user.username,
      method: 'Online',
      itemLabel: order.name,
    })
    showToast('Online order served ✓', 'success')
    setReceipt(receipt)
  }

  const openCancel = async (order) => {
    await cancelOrder(order.orderId)
    showToast('Order removed', 'info')
    setCancel({ order, chosen: null })
  }

  const reorder = (item) => {
    setCancel(null)
    openAccept(item)
  }

  return (
    <div className="board">
      <Panel title="Menu">
        <SectionLabel>Foods</SectionLabel>
        <div className="menu-grid">
          {foods.map((item) => (
            <ItemCard key={item.id} item={item} onAccept={() => openAccept(item)} />
          ))}
        </div>
        <SectionLabel>Drinks</SectionLabel>
        <div className="menu-grid">
          {drinks.map((item) => (
            <ItemCard key={item.id} item={item} onAccept={() => openAccept(item)} />
          ))}
        </div>
      </Panel>

      <Panel title="Ordered">
        {orders.length === 0 ? (
          <EmptyHint>No active orders yet</EmptyHint>
        ) : (
          <div className="ordered-list">
            {orders.map((o) => (
              <OrderCard
                key={o.orderId}
                order={o}
                onCancel={() => openCancel(o)}
                onPay={() => openPay(o)}
                onServe={() => serveOnline(o)}
              />
            ))}
          </div>
        )}
      </Panel>

      <AcceptModal accept={accept} ready={acceptReady} onClose={() => setAccept(null)} onPick={setAccept} onConfirm={confirmAccept} />
      <PayModal paying={paying} onClose={() => setPaying(null)} onPick={setPaying} onConfirm={confirmPay} onScanQr={() => setQrOpen(true)} />
      <CancelModal cancel={cancel} onClose={() => setCancel(null)} onPick={reorder} foods={foods} drinks={drinks} />
      <ReceiptModal receipt={receipt} onClose={() => setReceipt(null)} />
      <QRScanner open={qrOpen} onClose={() => setQrOpen(false)} onScan={handleQrScan} />
      <QrLogModal data={qrScanLog} onClose={() => setQrScanLog(null)} />
    </div>
  )
}

/* ------------------------------- sub-parts ------------------------------ */

function ItemCard({ item, onAccept }) {
  return (
    <div className="item-card">
      <div className="item-head">
        <span className="item-name">{item.name}</span>
        <span className="item-emoji">{item.emoji}</span>
      </div>
      <div className="item-price">{item.price} birr</div>
      <button className="accept-btn" onClick={onAccept}>
        Accept
      </button>
    </div>
  )
}

function OrderCard({ order, onCancel, onPay, onServe }) {
  const isOnline = order.source === 'online'
  const ready = !!order.ready
  return (
    <div className={`order-card ${isOnline ? 'online' : ''} ${ready ? 'ready' : ''}`}>
      <div className="order-top">
        <div>
          <div className="order-name">
            {order.emoji} {order.name}
          </div>
          <div className="order-meta">
            {isOnline ? 'Online order' : `Table ${order.table} · ${order.side}`}
          </div>
        </div>
        <div className="order-id">{order.orderId}</div>
      </div>
      <div className="order-badges">
        <span className="qty-box">×{order.qty}</span>
        <span className="badge">{order.total} birr</span>
        {isOnline && <span className="badge online">Online</span>}
        {ready ? (
          <span className="badge ready">Ready</span>
        ) : (
          <span className="badge preparing">Preparing…</span>
        )}
      </div>
      <div className="order-actions">
        {!ready && (
          <button className="mini-btn cancel" onClick={onCancel}>
            Cancel
          </button>
        )}
        <button
          className={`mini-btn pay ${ready ? 'pay-ready' : 'preparing'}`}
          onClick={onPay}
          disabled={!ready}
          title={ready ? 'Kitchen finished — collect payment' : 'Waiting for the kitchen'}
        >
          {ready ? 'Pay' : 'Preparing'}
        </button>
      </div>
    </div>
  )
}

function AcceptModal({ accept, ready, onClose, onPick, onConfirm }) {
  return (
    <Modal open={!!accept} onClose={onClose} title={accept?.item?.name?.toUpperCase()} subtitle="Select table, quantity & preparation">
      <div className="modal-section-label">Table</div>
      <div className="grid-4">
        {(accept?.tables || []).map((t) => (
          <div key={t} className={`pick-box ${accept?.table === t ? 'selected' : ''}`} onClick={() => onPick({ ...accept, table: t })}>
            {t}
          </div>
        ))}
      </div>
      <div className="modal-section-label">Quantity</div>
      <div className="grid-4">
        {[1, 2, 3, 4].map((q) => (
          <div key={q} className={`pick-box ${accept?.qty === q ? 'selected' : ''}`} onClick={() => onPick({ ...accept, qty: q })}>
            {q}
          </div>
        ))}
      </div>
      <div className="modal-section-label">Serve with</div>
      <div className="grid-2">
        {SIDES.map((s) => (
          <div key={s} className={`pick-box ${accept?.side === s ? 'selected' : ''}`} onClick={() => onPick({ ...accept, side: s })}>
            {s}
          </div>
        ))}
      </div>
      <button className="modal-primary-btn" disabled={!ready} onClick={onConfirm}>
        Order
      </button>
    </Modal>
  )
}

function PayModal({ paying, onClose, onPick, onConfirm, onScanQr }) {
  const o = paying?.order
  const loc = o?.source === 'online' ? 'Online order' : `Table ${o?.table}`
  return (
    <Modal open={!!paying} onClose={onClose} title="PAYMENT" subtitle={o && `${o.name} ×${o.qty} · ${loc} · Total ${o.total} birr`}>
      <div className="modal-section-label">Method</div>
      <div className="grid-2">
        {PAY_METHODS.map((m) => (
          <div key={m} className={`pick-box pay-method ${paying?.method === m ? 'selected' : ''}`} onClick={() => onPick({ ...paying, method: m })}>
            {m}
          </div>
        ))}
      </div>

      {paying?.method && (
        <>
          <button className="qr-scan-btn" onClick={onScanQr}>
            📷 Scan QR Code
          </button>
          {paying?.qrData && (
            <div style={{ marginTop: 8, padding: '6px 10px', background: 'rgba(106,154,109,0.1)', border: '1px solid var(--ready)', borderRadius: 8, fontSize: 11, color: 'var(--ready)' }}>
              ✓ QR scanned: <span style={{ fontFamily: 'monospace', color: 'var(--text)' }}>{paying.qrData.slice(0, 60)}{paying.qrData.length > 60 ? '...' : ''}</span>
            </div>
          )}
        </>
      )}

      <button className="modal-primary-btn" disabled={!paying?.method} onClick={onConfirm} style={{ marginTop: 12 }}>
        Pay &amp; Print
      </button>
    </Modal>
  )
}

function CancelModal({ cancel, onClose, onPick, foods, drinks }) {
  return (
    <Modal open={!!cancel} onClose={onClose} title="ORDER CANCELED" subtitle={cancel && `"${cancel.order.name}" (Table ${cancel.order.table}) was removed`}>
      <div className="section-label" style={{ marginTop: 2 }}>
        Foods
      </div>
      <div className="reorder-grid">
        {foods.filter((m) => m.name !== cancel?.order?.name).map((m) => (
          <div key={m.id} className="reorder-item" onClick={() => onPick(m)}>
            <div className="rn">
              {m.emoji} {m.name}
            </div>
            <div className="rp">{m.price} birr</div>
          </div>
        ))}
      </div>
      <div className="section-label">Drinks</div>
      <div className="reorder-grid">
        {drinks.filter((m) => m.name !== cancel?.order?.name).map((m) => (
          <div key={m.id} className="reorder-item" onClick={() => onPick(m)}>
            <div className="rn">
              {m.emoji} {m.name}
            </div>
            <div className="rp">{m.price} birr</div>
          </div>
        ))}
      </div>
    </Modal>
  )
}

function ReceiptModal({ receipt, onClose }) {
  if (!receipt) return null
  const lines = [
    { label: 'Waiter', value: receipt.waiter },
    { label: 'Table', value: receipt.table },
    { label: 'Order ID', value: receipt.orderId },
    { label: 'Item ID', value: receipt.itemId },
    { label: 'Item', value: receipt.item },
    { label: 'Quantity', value: `×${receipt.qty}` },
    { label: 'Time', value: receipt.time },
    { label: 'Payment', value: receipt.payment },
  ]
  if (receipt.qrData) {
    lines.push({ label: 'QR Data', value: receipt.qrData.slice(0, 40) + (receipt.qrData.length > 40 ? '...' : '') })
  }
  return (
    <Modal open={!!receipt} onClose={onClose} maxWidth={340}>
      <Receipt lines={lines} total={receipt.total} />
      <button className="modal-primary-btn" onClick={onClose}>
        Finished
      </button>
    </Modal>
  )
}

function QrLogModal({ data, onClose }) {
  if (!data) return null
  return (
    <Modal open={!!data} onClose={onClose} title="QR SCAN LOG" subtitle="Payment QR scan details" maxWidth={380}>
      <div style={{ padding: '12px', background: 'var(--card)', borderRadius: 10, border: '1px solid var(--hair)' }}>
        <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 4 }}>Order</div>
        <div style={{ fontSize: 13, color: 'var(--text)', marginBottom: 8 }}>{data.orderName} · {data.total} birr</div>
        <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 4 }}>Payment Method</div>
        <div style={{ fontSize: 13, color: 'var(--gold)', marginBottom: 8 }}>{data.method}</div>
        <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 4 }}>QR Content</div>
        <div style={{ fontSize: 12, color: 'var(--text)', fontFamily: 'monospace', wordBreak: 'break-all', padding: '8px', background: 'rgba(0,0,0,0.3)', borderRadius: 6, marginBottom: 8 }}>{data.qrData}</div>
        <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 4 }}>Scanned At</div>
        <div style={{ fontSize: 13, color: 'var(--text)' }}>{data.time}</div>
      </div>
      <button className="modal-primary-btn" onClick={onClose} style={{ marginTop: 12 }}>
        Close
      </button>
    </Modal>
  )
}
