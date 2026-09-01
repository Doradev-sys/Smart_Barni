import { Panel, EmptyHint } from '../../components/ui'
import { useAppData } from '../../context/AppDataContext'
import { useToast } from '../../context/ToastContext'

export default function OnlinePage() {
  const { queue, acceptOnline, declineOnline } = useAppData()
  const { showToast } = useToast()

  const handleAccept = async (qid) => {
    await acceptOnline(qid)
    showToast('Order accepted — moved to Ordered', 'success')
  }

  const handleDecline = async (qid) => {
    await declineOnline(qid)
    showToast('Order declined', 'info')
  }

  return (
    <div className="board single">
      <Panel title="Incoming Orders">
        {queue.length === 0 ? (
          <EmptyHint>No incoming customer orders</EmptyHint>
        ) : (
          <div className="queue-grid">
            {queue.map((q) => (
              <div className="queue-card" key={q.qid}>
                <div className="queue-top">
                  <span className="queue-name">
                    {q.emoji} {q.name}
                  </span>
                  <span className="queue-id">{q.qid}</span>
                </div>
                <div className="queue-meta">
                  {q.side} · ×{q.qty} · {q.total} birr
                </div>
                <span className="queue-badge">Online</span>
                <div className="queue-actions">
                  <button className="mini-btn decline" onClick={() => handleDecline(q.qid)}>
                    Decline
                  </button>
                  <button className="mini-btn order" onClick={() => handleAccept(q.qid)}>
                    Accept
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Panel>
    </div>
  )
}
