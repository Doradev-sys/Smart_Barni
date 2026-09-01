import { useMemo, useState, useEffect } from 'react'
import { Panel } from '../components/ui'
import { useAppData } from '../context/AppDataContext'
import { useAuth } from '../context/AuthContext'
import { businessDayKey } from '../utils/date'

const HOUR_LABELS = Array.from({ length: 24 }, (_, i) => {
  const h = (5 + i) % 24
  const ampm = h < 12 ? 'am' : 'pm'
  const hh = h % 12 === 0 ? 12 : h % 12
  return `${hh}${ampm}`
})

const PIE_COLORS = ['#f5d020', '#6a9a6d', '#e07a3a', '#5b8bd4', '#d45b8b', '#8b5bd4', '#5bd4c3', '#d4a55b']

export default function HistoryPage() {
  const { getHistoryDays, getHistory } = useAppData()
  const { user } = useAuth()
  const role = user?.role

  const days = useMemo(() => getHistoryDays(), [getHistoryDays])
  const [selected, setSelected] = useState(businessDayKey())
  const [day, setDay] = useState({ day: businessDayKey(), label: '', isToday: true, orders: [], kitchen: [], receipts: [] })

  useEffect(() => {
    let cancelled = false
    getHistory(selected).then((d) => {
      if (!cancelled) setDay(d)
    })
    return () => { cancelled = true }
  }, [getHistory, selected])

  const yesterday = useMemo(() => {
    const t = new Date()
    t.setDate(t.getDate() - 1)
    return businessDayKey(t)
  }, [])

  const selectDay = (key) => {
    if (key) setSelected(key)
  }

  const stats = useMemo(() => buildStats(day, role), [day, role])
  const chart = useMemo(() => buildChart(day, role), [day, role])
  const topItems = useMemo(() => buildTopItems(day, role), [day, role])
  const recos = useMemo(() => buildRecommendations(day, role, stats), [day, role, stats])
  const pieData = useMemo(() => buildPieData(topItems), [topItems])

  return (
    <div className="board single">
      <Panel>
        <div className="history-head">
          <div className="panel-title">Shift History</div>
          <div className="day-picker">
            <button className={`day-chip ${selected === businessDayKey() ? 'active' : ''}`} onClick={() => selectDay(businessDayKey())}>
              Today
            </button>
            <button className={`day-chip ${selected === yesterday ? 'active' : ''}`} onClick={() => selectDay(yesterday)}>
              Yesterday
            </button>
            <input
              type="date"
              className="date-input"
              value={selected}
              min={days[0]?.day}
              max={businessDayKey()}
              onChange={(e) => selectDay(e.target.value)}
            />
          </div>
        </div>

        <div className="history-meta">
          {day.isToday && <span className="live-dot" />}
          <span>
            {day.label} {day.isToday ? '· Live shift (5 AM – now)' : '· 5 AM shift'}
          </span>
        </div>

        <div className="reports-summary">
          {stats.cards.map((c) => (
            <div className="summary-card" key={c.label}>
              <div className="summary-icon">{c.icon}</div>
              <div className="summary-label">{c.label}</div>
              <div className="summary-value">{c.value}</div>
            </div>
          ))}
        </div>

        <div className="history-layout">
          <div>
            <div className="panel-title">Activity by Hour</div>
            <div className="bar-chart">
              {chart.data.map((v, i) => (
                <div className={`bar-col ${chart.maxIdx === i ? 'peak' : ''}`} key={i}>
                  <div className="bar" style={{ height: `${v.pct}%`, background: v.pct > 4 ? 'linear-gradient(180deg, var(--gold), var(--gold-dim))' : 'var(--hair)' }} data-value={v.value ? `${v.value}` : ''} />
                  <div className="bar-label">{i % 4 === 0 ? HOUR_LABELS[i] : ''}</div>
                </div>
              ))}
            </div>
            <div className="history-meta" style={{ marginTop: 10 }}>
              {chart.metric} · busiest at {chart.maxLabel}
            </div>
          </div>

          <div>
            <div className="panel-title">Top Performance</div>
            {topItems.length === 0 ? (
              <div className="reco-empty">No activity recorded for this day</div>
            ) : (
              <>
                {pieData && <DonutChart data={pieData} />}
                <div className="top-list">
                  {topItems.map((t, i) => (
                    <div className="top-row" key={t.name}>
                      <span className="top-rank" style={{ background: PIE_COLORS[i % PIE_COLORS.length] }}>{i + 1}</span>
                      <span className="top-name">{t.emoji} {t.name}</span>
                      <span className="top-val">{t.count}×</span>
                      <div className="top-track">
                        <span style={{ width: `${(t.count / topItems[0].count) * 100}%`, background: PIE_COLORS[i % PIE_COLORS.length] }} />
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>

        <div className="panel-title panel-gap">Recommendations</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {recos.map((r, i) => (
            <div className="reco-card" key={i}>
              <span className="reco-emoji">{r.icon}</span>
              <span>{r.text}</span>
            </div>
          ))}
          {recos.length === 0 && <div className="reco-empty">Make a few orders today and tomorrow you'll get smart suggestions here.</div>}
        </div>

        <div className="panel-title panel-gap">Full Activity</div>
        <div className="history-table-wrap">
          {role === 'kitchen' ? (
            <KitchenTable rows={day.kitchen} />
          ) : (
            <OrdersTable rows={day.orders} />
          )}
          {role === 'admin' && <KitchenTable rows={day.kitchen} title="Kitchen prep log" />}
        </div>
      </Panel>
    </div>
  )
}

function DonutChart({ data }) {
  const total = data.segments.reduce((s, seg) => s + seg.value, 0)
  if (total === 0) return null

  let accumulated = 0
  const gradientParts = data.segments.map((seg) => {
    const start = accumulated
    accumulated += (seg.value / total) * 360
    return `${seg.color} ${start}deg ${accumulated}deg`
  })
  const gradient = `conic-gradient(${gradientParts.join(', ')})`

  return (
    <div className="donut-chart-wrap">
      <div className="donut-ring" style={{ background: gradient }}>
        <div className="donut-hole">
          <div className="donut-total">{total}</div>
          <div className="donut-label">{data.label}</div>
        </div>
      </div>
      <div className="donut-legend">
        {data.segments.map((seg, i) => (
          <div className="donut-legend-item" key={i}>
            <span className="donut-legend-dot" style={{ background: seg.color }} />
            <span className="donut-legend-text">{seg.name}</span>
            <span className="donut-legend-val">{seg.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ------------------------------ tables ----------------------------------- */

function OrdersTable({ rows }) {
  if (rows.length === 0) return <div className="empty-hint">No sales recorded for this day</div>
  return (
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
        {rows.map((r, i) => (
          <tr key={i} className={r.declined ? 'declined' : ''}>
            <td>{r.name}</td>
            <td>{r.table}</td>
            <td>{r.orderType}</td>
            <td>{r.payment}{r.qrData ? <span className="qr-link" style={{ marginLeft: 4 }}>QR ✓</span> : null}</td>
            <td>{r.time}</td>
            <td>{r.price} birr</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function KitchenTable({ rows, title }) {
  if (rows.length === 0) {
    return title ? (
      <>
        <div className="section-label">{title}</div>
        <div className="empty-hint">Nothing prepared on this day</div>
      </>
    ) : (
      <div className="empty-hint">Nothing prepared on this day</div>
    )
  }
  return (
    <>
      {title && <div className="section-label">{title}</div>}
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
          {rows.map((r, i) => (
            <tr key={i}>
              <td>{r.name}</td>
              <td>×{r.qty}</td>
              <td>{r.side}</td>
              <td>{r.time}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}

/* ---------------------------- computations ------------------------------- */

function baseName(n) {
  return n.replace(/\s×\d+$/, '')
}

function hourOf(time) {
  const m = String(time).match(/(\d{1,2}):(\d{2})\s*(AM|PM)?/i)
  if (!m) return 12
  let h = +m[1]
  if (m[3] && /pm/i.test(m[3]) && h < 12) h += 12
  if (m[3] && /am/i.test(m[3]) && h === 12) h = 0
  return h
}

function bucketOf(hour) {
  return (hour - 5 + 24) % 24
}

function buildStats(day, role) {
  const orders = day.orders || []
  const kitchen = day.kitchen || []
  const cards = []

  if (role === 'kitchen') {
    const portions = kitchen.reduce((s, r) => s + (r.qty || 1), 0)
    cards.push({ icon: '🍽️', label: 'Items prepared', value: kitchen.length })
    cards.push({ icon: '📦', label: 'Total portions', value: portions })
    cards.push({ icon: '⏰', label: 'Busiest hour', value: busiestHourLabel(kitchen.map((k) => k.time)) })
  } else {
    const finished = orders.filter((o) => !o.declined)
    const revenue = finished.reduce((s, o) => s + o.price, 0)
    const online = orders.filter((o) => o.orderType === 'Online' && !o.declined).length
    const declined = orders.filter((o) => o.declined).length
    cards.push({ icon: '🛒', label: 'Orders', value: orders.length })
    cards.push({ icon: '💰', label: 'Revenue', value: `${revenue} birr` })
    cards.push({ icon: '🌐', label: 'Online', value: online })
    cards.push({ icon: '🚫', label: 'Declined', value: declined })
    if (role === 'admin') {
      const portions = kitchen.reduce((s, r) => s + (r.qty || 1), 0)
      cards.push({ icon: '👨‍🍳', label: 'Kitchen prepped', value: portions })
    }
  }
  return { cards }
}

function busiestHourLabel(times) {
  const counts = Array(24).fill(0)
  times.forEach((t) => {
    const h = hourOf(t)
    counts[bucketOf(h)] += 1
  })
  const max = Math.max(...counts)
  if (max === 0) return '—'
  return HOUR_LABELS[counts.indexOf(max)]
}

function buildChart(day, role) {
  const values = Array(24).fill(0)
  if (role === 'kitchen') {
    ;(day.kitchen || []).forEach((k) => {
      values[bucketOf(hourOf(k.time))] += k.qty || 1
    })
  } else {
    ;(day.orders || [])
      .filter((o) => !o.declined)
      .forEach((o) => {
        values[bucketOf(hourOf(o.time))] += role === 'admin' ? o.price : 1
      })
  }
  const max = Math.max(...values)
  const maxIdx = max > 0 ? values.indexOf(max) : -1
  return {
    metric: role === 'kitchen' ? 'portions prepared per hour' : role === 'admin' ? 'revenue (birr) per hour' : 'orders finished per hour',
    maxLabel: maxIdx === -1 ? '—' : HOUR_LABELS[maxIdx],
    maxIdx,
    values,
    data: values.map((v) => ({
      value: v,
      pct: max > 0 ? Math.max(4, (v / max) * 100) : 4,
    })),
  }
}

function buildTopItems(day, role) {
  const map = new Map()
  if (role === 'kitchen') {
    ;(day.kitchen || []).forEach((k) => {
      const name = k.name
      const cur = map.get(name) || { name, emoji: emojiOf(name), count: 0 }
      cur.count += k.qty || 1
      map.set(name, cur)
    })
  } else {
    ;(day.orders || [])
      .filter((o) => !o.declined)
      .forEach((o) => {
        const name = baseName(o.name)
        const cur = map.get(name) || { name, emoji: emojiOf(name), count: 0 }
        cur.count += 1
        map.set(name, cur)
      })
  }
  return [...map.values()].sort((a, b) => b.count - a.count).slice(0, 5)
}

function buildPieData(topItems) {
  if (topItems.length === 0) return null
  const label = topItems.length === 1 ? 'order' : 'orders'
  return {
    label,
    segments: topItems.map((t, i) => ({
      name: t.name,
      value: t.count,
      color: PIE_COLORS[i % PIE_COLORS.length],
    })),
  }
}

function emojiOf(name) {
  const n = name.toLowerCase()
  if (n.includes('coffee') || n.includes('espresso') || n.includes('cappuccino')) return '☕'
  if (n.includes('burger')) return '🍔'
  if (n.includes('fries')) return '🍟'
  if (n.includes('pizza')) return '🍕'
  if (n.includes('pasta')) return '🍝'
  if (n.includes('chicken')) return '🍗'
  if (n.includes('sandwich')) return '🥪'
  if (n.includes('salad')) return '🥗'
  if (n.includes('steak')) return '🥩'
  if (n.includes('sushi')) return '🍣'
  if (n.includes('wrap')) return '🌯'
  if (n.includes('juice')) return '🥤'
  if (n.includes('mojito')) return '🍹'
  if (n.includes('tea')) return '🧋'
  if (n.includes('chocolate')) return '🍫'
  return '🫘'
}

function buildRecommendations(day, role, stats) {
  const recos = []
  const orders = day.orders || []
  const kitchen = day.kitchen || []

  if (role === 'kitchen') {
    const top = buildTopItems(day, 'kitchen')[0]
    if (top) {
      recos.push({
        icon: '👨‍🍳',
        text: <><b>{top.name}</b> was your most-prepared item ({top.count} portions) — keep that ingredient stock topped up first.</>,
      })
    }
    const peak = busiestHourLabel(kitchen.map((k) => k.time))
    if (peak !== '—') {
      recos.push({
        icon: '⏰',
        text: <>Preps peaked around <b>{peak}</b> — prep your mise-en-place just before that window.</>,
      })
    }
    return recos
  }

  const finished = orders.filter((o) => !o.declined)
  const top = buildTopItems(day, 'waiter')[0]
  const revenue = finished.reduce((s, o) => s + o.price, 0)
  const peak = busiestHourLabel(finished.map((o) => o.time))

  if (top) {
    recos.push({
      icon: '🏆',
      text: <><b>{top.name}</b> was your top seller ({top.count} orders) — try a combo offer around it to lift the average bill.</>,
    })
  }
  if (peak !== '—') {
    recos.push({
      icon: '⏰',
      text: <>The busiest slot was <b>{peak}</b> ({chartCount(finished, peak)} orders) — make sure full coverage is on the floor then.</>,
    })
  }
  const onlineCount = finished.filter((o) => o.orderType === 'Online').length
  if (finished.length > 0) {
    const pct = Math.round((onlineCount / finished.length) * 100)
    if (pct >= 30) {
      recos.push({
        icon: '🌐',
        text: <>Online was <b>{pct}%</b> of sales — delivery is working, keep it promoted.</>,
      })
    } else if (finished.length >= 4) {
      recos.push({
        icon: '📣',
        text: <>Online was only <b>{pct}%</b> of sales — a small delivery special could open a new revenue stream.</>,
      })
    }
  }
  const declined = orders.filter((o) => o.declined).length
  if (declined > 0) {
    recos.push({
      icon: '🚫',
      text: <><b>{declined}</b> online order{declined > 1 ? 's were' : ' was'} declined — review stock and delivery coverage for that window.</>,
    })
  }
  if (finished.length > 0 && revenue > 0) {
    recos.push({
      icon: '💡',
      text: <>Average ticket was <b>{Math.round(revenue / finished.length)} birr</b> — upselling a side could raise it further.</>,
    })
  }
  return recos
}

function chartCount(orders, label) {
  const idx = HOUR_LABELS.indexOf(label)
  if (idx === -1) return 0
  return orders.filter((o) => bucketOf(hourOf(o.time)) === idx).length
}
