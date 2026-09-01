import { useState } from 'react'
import Receipt from '../../components/Receipt'
import { Panel, EmptyHint } from '../../components/ui'
import { useAppData } from '../../context/AppDataContext'

export default function AdminReceiptsPage() {
  const { receipts } = useAppData()
  const [index, setIndex] = useState(0)

  if (receipts.length === 0) {
    return (
      <div className="board single">
        <Panel title="Receipt Archive">
          <EmptyHint>No receipts yet — paid orders will appear here</EmptyHint>
        </Panel>
      </div>
    )
  }

  const current = Math.min(index, receipts.length - 1)
  const receipt = receipts[current]
  const prev = () => setIndex(Math.max(0, current - 1))
  const next = () => setIndex(Math.min(receipts.length - 1, current + 1))
  const progress = ((current + 1) / receipts.length) * 100

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
    lines.push({ label: 'QR Data', value: receipt.qrData.slice(0, 30) + (receipt.qrData.length > 30 ? '...' : '') })
  }

  return (
    <div className="board single">
      <Panel title="Receipt Archive">
        <div className="receipts-summary-row">
          <div className="summary-card">
            <div className="summary-label">Receipts issued</div>
            <div className="summary-value">{receipts.length}</div>
          </div>
          <div className="summary-card">
            <div className="summary-label">Collected total</div>
            <div className="summary-value">
              {receipts.reduce((s, r) => s + r.total, 0)} birr
            </div>
          </div>
        </div>

        <div className="receipt-carousel">
          <button className="carousel-btn" onClick={prev} disabled={current === 0} aria-label="Previous receipt">
            ‹
          </button>
          <div className="carousel-stage">
            <div className="carousel-receipt">
              <Receipt lines={lines} total={receipt.total} compact />
            </div>
            <div className="carousel-meta">
              <span className="carousel-counter">
                {current + 1} / {receipts.length}
              </span>
              <span>{receipt.id}</span>
            </div>
            <div className="carousel-progress">
              <span style={{ width: `${progress}%` }} />
            </div>
          </div>
          <button className="carousel-btn" onClick={next} disabled={current === receipts.length - 1} aria-label="Next receipt">
            ›
          </button>
        </div>
      </Panel>
    </div>
  )
}
