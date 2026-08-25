import { useEffect } from 'react'

export default function Modal({ open, onClose, title, subtitle, children, maxWidth = 380 }) {
  useEffect(() => {
    if (!open) return
    const onKey = (e) => e.key === 'Escape' && onClose?.()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  if (!open) return null

  return (
    <div className="overlay show" onMouseDown={(e) => e.target === e.currentTarget && onClose?.()}>
      <div className="modal modal-wrap" style={{ maxWidth }}>
        <button className="modal-close" onClick={onClose} aria-label="Close">
          &times;
        </button>
        {title && <div className="modal-title">{title}</div>}
        {subtitle && <div className="modal-sub">{subtitle}</div>}
        {children}
      </div>
    </div>
  )
}
