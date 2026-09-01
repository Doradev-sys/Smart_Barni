export function Panel({ title, action, children, className = '' }) {
  return (
    <section className={`panel ${className}`}>
      {title && (
        <div className="panel-title">
          {title}
          {action}
        </div>
      )}
      {children}
    </section>
  )
}

export function SectionLabel({ children }) {
  return <div className="section-label">{children}</div>
}

export function EmptyHint({ children }) {
  return <div className="empty-hint">{children}</div>
}

export function Badge({ children, tone }) {
  return <span className={`badge ${tone || ''}`}>{children}</span>
}
