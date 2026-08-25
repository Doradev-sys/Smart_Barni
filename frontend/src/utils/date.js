// Business-day helpers — a Barni "day" runs 5:00 AM → 4:59 AM the next morning.
// So a report created at 6 AM today belongs to today's shift, and one created at
// 3 AM tonight still belongs to yesterday's shift (lasts 24 hours from 5 AM).

const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

// The 5AM-shift key (YYYY-MM-DD) for a given Date.
export function businessDayKey(d = new Date()) {
  const t = new Date(d.getFullYear(), d.getMonth(), d.getDate(), d.getHours() - 5)
  const y = t.getFullYear()
  const m = String(t.getMonth() + 1).padStart(2, '0')
  const day = String(t.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

// First instant of the shift (5 AM) for a day key.
export function keyToDate(key) {
  const [y, m, d] = key.split('-').map(Number)
  return new Date(y, m - 1, d, 5, 0, 0)
}

// "Tue, Aug 12"
export function dayLabel(key) {
  const t = keyToDate(key)
  return `${WEEKDAYS[t.getDay()]}, ${MONTHS[t.getMonth()]} ${t.getDate()}`
}

// The last n shift-day keys (today first), oldest last.
export function lastNDays(n = 7) {
  const keys = []
  for (let i = 0; i < n; i++) {
    const t = new Date()
    t.setDate(t.getDate() - i)
    keys.push(businessDayKey(t))
  }
  return keys.reverse()
}
