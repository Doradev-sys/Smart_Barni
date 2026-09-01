import { useState } from 'react'
import Modal from '../../components/Modal'
import IssueCard from '../../components/IssueCard'
import IssueHistoryModal from '../../components/IssueHistoryModal'
import { Panel } from '../../components/ui'
import { useAppData } from '../../context/AppDataContext'
import { useAuth } from '../../context/AuthContext'
import { useToast } from '../../context/ToastContext'

export default function AdminReportsPage() {
  const { waiterReports, kitchenReports, receipts, issues, respondToIssue, resolveIssue } =
    useAppData()
  const { user } = useAuth()
  const { showToast } = useToast()

  const [historyOpen, setHistoryOpen] = useState(false)
  const [responding, setResponding] = useState(null) // issue being responded to
  const [draft, setDraft] = useState('')

  const revenue = receipts.reduce((s, r) => s + r.total, 0)
  const atBarni = waiterReports.filter((r) => r.orderType === 'At Barni').length
  const online = waiterReports.filter((r) => r.orderType === 'Online' && !r.declined).length
  const declined = waiterReports.filter((r) => r.declined).length

  const openIssues = issues.filter((i) => i.status !== 'resolved')

  const openRespond = (issue) => {
    setResponding(issue)
    setDraft(issue.response || '')
  }

  const sendResponse = async () => {
    if (!draft.trim()) return showToast('Write a response first', 'error')
    await respondToIssue(responding.id, draft.trim())
    setResponding(null)
    setDraft('')
    showToast('Response sent to staff ✓', 'success')
  }

  const markDone = async (issue) => {
    await resolveIssue(issue.id, user.username)
    showToast('Issue marked as resolved ✓', 'success')
  }

  return (
    <div className="board reports">
      <div>
        <Panel title="Activity Overview">
          <div className="admin-grid">
            <div className="summary-card">
              <div className="summary-label">Total orders today</div>
              <div className="summary-value">{waiterReports.length}</div>
            </div>
            <div className="summary-card">
              <div className="summary-label">Total revenue</div>
              <div className="summary-value">{revenue} birr</div>
            </div>
            <div className="summary-card">
              <div className="summary-label">At Barni</div>
              <div className="summary-value">{atBarni}</div>
            </div>
            <div className="summary-card">
              <div className="summary-label">Online</div>
              <div className="summary-value">{online}</div>
            </div>
            <div className="summary-card">
              <div className="summary-label">Declined</div>
              <div className="summary-value">{declined}</div>
            </div>
            <div className="summary-card">
              <div className="summary-label">Kitchen prepared</div>
              <div className="summary-value">{kitchenReports.length}</div>
            </div>
          </div>
        </Panel>

        <Panel title="Waiter Activity — Daily Sales" className="panel-gap">
          {waiterReports.length === 0 ? (
            <div className="empty-hint">No waiter sales recorded yet today</div>
          ) : (
            <table className="report-table">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Table</th>
                  <th>Type</th>
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
                    <td>{r.payment}</td>
                    <td>{r.time}</td>
                    <td>{r.price} birr</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Panel>

        <Panel title="Kitchen Activity — Prep Log" className="panel-gap">
          {kitchenReports.length === 0 ? (
            <div className="empty-hint">No kitchen activity recorded yet</div>
          ) : (
            <table className="report-table">
              <thead>
                <tr>
                  <th>Food</th>
                  <th>Qty</th>
                  <th>Served With</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {kitchenReports.map((r) => (
                  <tr key={r.orderId + r.time}>
                    <td>{r.name}</td>
                    <td>×{r.qty}</td>
                    <td>{r.side}</td>
                    <td>{r.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Panel>
      </div>

      <Panel
        title="Staff Reports"
        action={
          <button className="add-btn" onClick={() => setHistoryOpen(true)}>
            🕘 History
          </button>
        }
      >
        {openIssues.length === 0 ? (
          <div className="empty-hint">
            {issues.length > 0 ? 'All reports handled ✓' : 'No reports from staff yet'}
          </div>
        ) : (
          <div className="issue-list">
            {openIssues.map((i) => (
              <IssueCard
                key={i.id}
                issue={i}
                actions={{ onRespond: openRespond, onDone: markDone }}
              />
            ))}
          </div>
        )}
      </Panel>

      <Modal
        open={!!responding}
        onClose={() => setResponding(null)}
        title="WRITE RESPONSE"
        subtitle={responding && `${responding.role === 'kitchen' ? '🍳 Kitchen' : '🧑‍🍳 Waiter'} · ${responding.kind}`}
        maxWidth={360}
      >
        <div className="issue-detail response-context">{responding?.detail}</div>
        <textarea
          className="textarea-box"
          placeholder="Type your response to the staff member…"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
        />
        <button className="modal-primary-btn" onClick={sendResponse} disabled={!draft.trim()}>
          Send Response
        </button>
      </Modal>

      <IssueHistoryModal
        open={historyOpen}
        onClose={() => setHistoryOpen(false)}
        issues={issues}
        title="Staff Report History"
        subtitle="Every report from waiters and kitchen, in order"
      />
    </div>
  )
}
