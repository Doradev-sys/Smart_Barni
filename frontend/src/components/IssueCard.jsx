export default function IssueCard({ issue, actions }) {
  const roleIcon = issue.role === 'kitchen' ? '🍳' : '🧑‍🍳'

  return (
    <div className={`issue-card issue-${issue.priority?.toLowerCase() || 'normal'}`}>
      <div className="issue-top">
        <span className="issue-kind">
          {roleIcon} {issue.role === 'kitchen' ? 'Kitchen' : 'Waiter'} · {issue.kind}
        </span>
        <span className={`issue-status ${issue.status}`}>
          {issue.status === 'resolved' ? '✓ Resolved' : issue.status === 'responded' ? '↩ Responded' : 'Pending'}
        </span>
      </div>
      <div className="issue-meta">
        {issue.category && (
          <>
            {issue.category} · {issue.item} · <b>{issue.priority}</b> ·
          </>
        )}{' '}
        {issue.author} · {issue.time}
      </div>
      <div className="issue-detail">{issue.detail}</div>

      {issue.response && (
        <div className="issue-response">
          <div className="issue-response-title">Admin response · {issue.respondedTime}</div>
          <div className="issue-response-text">{issue.response}</div>
        </div>
      )}

      {issue.status === 'resolved' && (
        <div className="issue-meta resolved-meta">
          Resolved by {issue.resolvedBy} · {issue.resolvedTime}
        </div>
      )}

      {actions && issue.status !== 'resolved' && (
        <div className="issue-actions">
          <button className="mini-btn resp" onClick={() => actions.onRespond?.(issue)}>
            Response
          </button>
          <button className="mini-btn done" onClick={() => actions.onDone?.(issue)}>
            Done
          </button>
        </div>
      )}
    </div>
  )
}
