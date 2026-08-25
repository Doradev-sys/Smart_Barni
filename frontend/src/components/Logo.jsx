import { useMemo } from 'react'

export default function Logo({ onClick }) {
  const sparkles = useMemo(
    () => [
      { x: -6, y: -6, d: 0 },
      { x: 44, y: -10, d: 1.2 },
      { x: 76, y: 6, d: 2.4 },
      { x: 10, y: 26, d: 3.4 },
      { x: 96, y: -4, d: 4.4 },
      { x: 54, y: 22, d: 5.4 },
    ],
    []
  )

  return (
    <div className="brand" onClick={onClick} style={{ cursor: onClick ? 'pointer' : undefined }}>
      <div className="cup-3d">
        <svg width="42" height="42" viewBox="0 0 44 44" aria-hidden="true">
          <path className="steam-path steam-a" d="M15 12 q-2 -3 0 -6 q2 -3 0 -6" stroke="var(--gold-light)" strokeWidth="1.3" fill="none" strokeLinecap="round" />
          <path className="steam-path steam-b" d="M22 12 q-2 -3 0 -6 q2 -3 0 -6" stroke="var(--gold-light)" strokeWidth="1.3" fill="none" strokeLinecap="round" />
          <path d="M9 16 h20 v8 a10 10 0 0 1 -20 0 z" fill="var(--gold)" stroke="var(--gold-dim)" strokeWidth="1" />
          <rect x="8" y="14" width="22" height="3.5" rx="1.75" fill="var(--gold-light)" />
          <path d="M29 19 q6 -0.5 6 4.5 t-6 5" fill="none" stroke="var(--gold)" strokeWidth="1.6" strokeLinecap="round" />
          <path d="M13 34 q9 5 20 -1 q3 4 -2 6 q-13 4 -22 -2 q-2 -2 4 -3z" fill="none" stroke="var(--gold-dim)" strokeWidth="1" opacity=".55" />
        </svg>
      </div>
      <div className="sparkle-wrap">
        {sparkles.map((s, i) => (
          <span
            key={i}
            className="sparkle"
            style={{ left: s.x + 'px', top: s.y + 'px', animationDelay: s.d + 's' }}
          />
        ))}
      </div>
      <div className="logo-block">
        <div className="logo-text">Barni</div>
        <div className="logo-sub">Coffee</div>
      </div>
    </div>
  )
}
