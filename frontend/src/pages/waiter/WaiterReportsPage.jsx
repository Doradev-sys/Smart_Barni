import { useState } from 'react'
import Modal from '../../components/Modal'
import IssueHistoryModal from '../../components/IssueHistoryModal'
import { Panel } from '../../components/ui'
import { useAppData } from '../../context/AppDataContext'
import { useAuth } from '../../context/AuthContext'
import { useToast } from '../../context/ToastContext'

export default function WaiterReportsPage() {
  const { waiterReports, issues, submitIssue } = useAppData()
  const { user } = useAuth()
  const { showToast } = useToast()

  const [contactOpen, setContactOpen] = useState(false)
  const [historyOpen, setHistoryOpen] = useState(false)
  const [issue, setIssue] = useState({ kind: '', detail: '' })
  const [qrLog, setQrLog] = useState(null)

  const myIssues = issues.filter((i) => i.author === user.username)

  const finished = waiterReports.filter((r) => !r.declined)
  const total = finished.reduce((s, r) => s + r.price, 0)

  const submit = async () => {
    if (!issue.kind || !issue.detail.trim()) {
      return showToast('Select an issue and enter details', 'error')
    }
    await submitIssue({
      author: user.username,
      role: 'waiter',
      kind: issue.kind,
      detail: issue.detail.trim(),
    })
    setIssue({ kind: '', detail: '' })
    setContactOpen(false)
    showToast('Sent to Admin Panel ✓', 'success')
  }

  return (
    <div className="board reports">
      <Panel title="Daily Sales Report">
        <div className="reports-summary">
          <div className="summary-card">
            <div className="summary-label">Orders finished</div>
            <div className="summary-value">{finished.length}</div>
          </div>
          <div className="summary-card">
            <div className="summary-label">Total revenue</div>
            <div className="summary-value">{total} birr</div>
          </div>
        </div>

        {waiterReports.length === 0 ? (
          <div className="empty-hint">No finished orders yet today</div>
        ) : (
          <table className="report-table">
            <thead>
              <tr>
                <th>Item</th>
                <th>Table</th>
                <th>Order Type</th>
                <th>Payment</th>
                <th>Time</th>
                <th>Amount</th>
              </tr>
            </thead>
            <tbody>
              {waiterReports.map((r) => (
                <tr key={r.orderId + r.time} className={r.declined ? 'declined' : ''}>
                  <td>{r.name}</td>
                  <td>{r.table}</td>
                  <td>{r.orderType}</td>
                  <td>
                    {r.payment}
                    {r.qrData && (
                      <>
                        <br />
                        <span className="qr-link" title={r.qrData}>
                          QR: {r.qrData.slice(0, 20)}...
                        </span>
                        <button className="qr-log-btn" onClick={() => setQrLog(r)}>
                          Log
                        </button>
                      </>
                    )}
                  </td>
                  <td>{r.time}</td>
                  <td>{r.price} birr</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>

      <Panel title="Support">
        <div className="contact-miss-card" onClick={() => setContactOpen(true)}>
          <div className="cm-title">📩 CONTACT ADMIN</div>
        <div className="cm-sub">Waiter-side issue → admin</div>
        </div>
        <button className="history-btn" onClick={() => setHistoryOpen(true)}>
          🕘 My Report History
        </button>
        <div className="support-note">
          Reports you send stay in your history with live status — you'll see a green resolved
          badge the moment admin closes them.
        </div>
      </Panel>

      <Modal
        open={contactOpen}
        onClose={() => setContactOpen(false)}
        title="CONTACT ADMIN"
        maxWidth={320}
      >
        <div className="modal-section-label">Issue</div>
        <select
          className="select-box"
          value={issue.kind}
          onChange={(e) => setIssue((i) => ({ ...i, kind: e.target.value }))}
        >
          <option value="">Select report</option>
          <option value="Complain">Complain</option>
          <option value="Missing">Missing</option>
          <option value="Permission">Permission</option>
          <option value="Other">Other</option>
        </select>
        <textarea
          className="textarea-box"
          placeholder="Enter the detail"
          value={issue.detail}
          onChange={(e) => setIssue((i) => ({ ...i, detail: e.target.value }))}
        />
        <button className="modal-primary-btn" onClick={submit}>
          Submit
        </button>
      </Modal>

      <IssueHistoryModal
        open={historyOpen}
        onClose={() => setHistoryOpen(false)}
        issues={myIssues}
        title="My Report History"
        subtitle="Everything you reported, whenever you reported it"
      />

      <QrLogModal data={qrLog} onClose={() => setQrLog(null)} />
    </div>
  )
}

function QrLogModal({ data, onClose }) {
  if (!data) return null
  return (
    <Modal open={!!data} onClose={onClose} title="QR SCAN LOG" subtitle="Payment QR scan details" maxWidth={380}>
      <div style={{ padding: '12px', background: 'var(--card)', borderRadius: 10, border: '1px solid var(--hair)' }}>
        <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 4 }}>Order</div>
        <div style={{ fontSize: 13, color: 'var(--text)', marginBottom: 8 }}>{data.name} · {data.price} birr</div>
        <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 4 }}>Payment Method</div>
        <div style={{ fontSize: 13, color: 'var(--gold)', marginBottom: 8 }}>{data.payment}</div>
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
