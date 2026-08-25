import { useMemo, useState } from 'react'
import Modal from '../../components/Modal'
import IssueHistoryModal from '../../components/IssueHistoryModal'
import { Panel } from '../../components/ui'
import { useAppData } from '../../context/AppDataContext'
import { useAuth } from '../../context/AuthContext'
import { useToast } from '../../context/ToastContext'
import { INGREDIENTS } from '../../data/menu'

export default function KitchenReportsPage() {
  const { kitchenReports, issues, submitIssue } = useAppData()
  const { user } = useAuth()
  const { showToast } = useToast()

  const [open, setOpen] = useState(false)
  const [historyOpen, setHistoryOpen] = useState(false)
  const [form, setForm] = useState({
    kind: '',
    detail: '',
    category: null,
    item: '',
    priority: null,
  })

  const myIssues = issues.filter((i) => i.author === user.username)
  const totalPrepared = kitchenReports.reduce((s, r) => s + r.qty, 0)

  const stockOptions = useMemo(() => {
    if (!form.category) return []
    const names = new Set()
    Object.values(INGREDIENTS).forEach((ing) =>
      ing[form.category].forEach((i) => names.add(i.n))
    )
    return [...names]
  }, [form.category])

  const submit = async () => {
    if (!form.kind || !form.detail.trim()) {
      return showToast('Select a report type and enter details', 'error')
    }
    if (form.kind === 'Low stock' && (!form.category || !form.priority)) {
      return showToast('Select category and priority', 'error')
    }
    await submitIssue({
      author: user.username,
      role: 'kitchen',
      kind: form.kind,
      category: form.category,
      item: form.item,
      priority: form.priority,
      detail: form.detail.trim(),
    })
    setOpen(false)
    setForm({ kind: '', detail: '', category: null, item: '', priority: null })
    showToast('Sent to Admin Panel ✓', 'success')
  }

  return (
    <div className="board reports">
      <Panel title="Kitchen Prep Report">
        <div className="reports-summary">
          <div className="summary-card">
            <div className="summary-label">Items prepared</div>
            <div className="summary-value">{kitchenReports.length}</div>
          </div>
          <div className="summary-card">
            <div className="summary-label">Total portions</div>
            <div className="summary-value">{totalPrepared}</div>
          </div>
        </div>

        {kitchenReports.length === 0 ? (
          <div className="empty-hint">Nothing prepared yet</div>
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

      <Panel title="Support">
        <div className="contact-miss-card" onClick={() => setOpen(true)}>
          <div className="cm-title">📋 KITCHEN REPORT</div>
          <div className="cm-sub">Missing item, low stock, permission…</div>
        </div>
        <button className="history-btn" onClick={() => setHistoryOpen(true)}>
          🕘 My Report History
        </button>
        <div className="support-note">
          Reports you send stay in your history with live status — you'll see a green resolved
          badge the moment admin closes them.
        </div>
      </Panel>

      <Modal open={open} onClose={() => setOpen(false)} title="KITCHEN REPORT" maxWidth={340}>
        <div className="modal-section-label">Type</div>
        <select
          className="select-box"
          value={form.kind}
          onChange={(e) => setForm((f) => ({ ...f, kind: e.target.value }))}
        >
          <option value="">Select report</option>
          <option value="Missing item">Missing item</option>
          <option value="Low stock">Low stock</option>
          <option value="Permission">Permission</option>
          <option value="Other">Other</option>
        </select>

        {form.kind === 'Low stock' && (
          <>
            <div className="modal-section-label">Category</div>
            <div className="grid-2">
              {['raw', 'processed'].map((c) => (
                <div
                  key={c}
                  className={`pick-box ${form.category === c ? 'selected' : ''}`}
                  onClick={() => setForm((f) => ({ ...f, category: c, item: '' }))}
                >
                  {c === 'raw' ? 'Raw' : 'Processed'}
                </div>
              ))}
            </div>
            <div className="modal-section-label">Ingredient</div>
            <select
              className="select-box"
              value={form.item}
              onChange={(e) => setForm((f) => ({ ...f, item: e.target.value }))}
            >
              <option value="">{form.category ? 'Select ingredient' : 'Select category first'}</option>
              {stockOptions.map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
            <div className="modal-section-label">Priority</div>
            <div className="grid-3">
              {[
                { label: 'Urgent', cls: 'pri-red' },
                { label: 'Medium', cls: 'pri-yellow' },
                { label: 'Low', cls: 'pri-green' },
              ].map((p) => (
                <div
                  key={p.label}
                  className={`pick-box ${p.cls} ${form.priority === p.label ? 'selected' : ''}`}
                  onClick={() => setForm((f) => ({ ...f, priority: p.label }))}
                >
                  {p.label}
                </div>
              ))}
            </div>
          </>
        )}

        <textarea
          className="textarea-box"
          placeholder="Enter the detail"
          value={form.detail}
          onChange={(e) => setForm((f) => ({ ...f, detail: e.target.value }))}
        />
        <button className="modal-primary-btn" onClick={submit}>
          Submit to Admin
        </button>
      </Modal>

      <IssueHistoryModal
        open={historyOpen}
        onClose={() => setHistoryOpen(false)}
        issues={myIssues}
        title="My Report History"
        subtitle="Everything you reported, whenever you reported it"
      />
    </div>
  )
}
