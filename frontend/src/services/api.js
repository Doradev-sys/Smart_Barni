// ===========================================================================
// Barni Coffee — API service layer (real Django REST backend)
// ===========================================================================

import { businessDayKey, dayLabel, lastNDays } from '../utils/date'

const BASE = '/api'

/* ------------------------------- helpers -------------------------------- */

function getToken() {
  return localStorage.getItem('barni_access')
}

function getRefreshToken() {
  return localStorage.getItem('barni_refresh')
}

function setTokens(access, refresh) {
  localStorage.setItem('barni_access', access)
  if (refresh) localStorage.setItem('barni_refresh', refresh)
}

function clearTokens() {
  localStorage.removeItem('barni_access')
  localStorage.removeItem('barni_refresh')
}

async function apiCall(method, path, body, auth = true) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth && getToken()) {
    headers['Authorization'] = `Bearer ${getToken()}`
  }
  const opts = { method, headers }
  if (body) opts.body = JSON.stringify(body)

  let res = await fetch(`${BASE}${path}`, opts)

  if (res.status === 401 && auth && getRefreshToken()) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      headers['Authorization'] = `Bearer ${getToken()}`
      res = await fetch(`${BASE}${path}`, { ...opts, headers })
    }
  }

  const data = await res.json().catch(() => null)
  if (!res.ok) {
    const msg =
      (data && (data.detail || data.error || data.non_field_errors?.[0])) ||
      'Request failed'
    throw new Error(msg)
  }
  return data
}

async function refreshAccessToken() {
  try {
    const res = await fetch(`${BASE}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: getRefreshToken() }),
    })
    if (!res.ok) {
      clearTokens()
      return false
    }
    const data = await res.json()
    setTokens(data.access, data.refresh || getRefreshToken())
    return true
  } catch {
    clearTokens()
    return false
  }
}

function now() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })
}

function todayISO() {
  return new Date().toISOString().split('T')[0]
}

/* ------------------------------- auth ----------------------------------- */

export const api = {
  async login({ username, password, role }) {
    const data = await apiCall('POST', '/auth/login/', {
      username,
      password,
      role,
    }, false)
    setTokens(data.access, data.refresh)
    const u = data.user
    let profilePicture = u.profile_picture || ''
    if (!profilePicture) {
      try {
        const me = await apiCall('GET', '/auth/me/')
        profilePicture = me.profile_picture || ''
      } catch {}
    }
    return {
      role: u.role.toLowerCase(),
      username: u.username,
      fullName: u.full_name || u.username,
      profilePicture,
      tables: [],
    }
  },

  async register({ fullName, fatherName, phone, username, password, role, email, full_name, father_name }) {
    await apiCall('POST', '/auth/register/', {
      username,
      password,
      role: role || 'Waiter',
      full_name: full_name || fullName || '',
      father_name: father_name || fatherName || '',
      phone: phone || '',
      email: email || '',
    }, false)
    return { ok: true }
  },

  async registerCustomer({ username, password, fullName, phone }) {
    await apiCall('POST', '/auth/register/', {
      username,
      password,
      role: 'Customer',
      full_name: fullName || username,
      phone: phone || '',
    }, false)
    return { ok: true }
  },

  async resetPassword({ username, password }) {
    return { ok: true }
  },

  /* ---------------------------- live state ------------------------------ */

  async getState() {
    try {
      const [ordersRaw, kitchenRaw, receiptsRaw, tablesRaw, kitchenHistoryRaw, alertsRaw] =
        await Promise.all([
          apiCall('GET', '/orders/orders/').catch(() => []),
          apiCall('GET', '/kitchen/queue/').catch(() => []),
          apiCall('GET', '/orders/receipts/').catch(() => []),
          apiCall('GET', '/orders/tables/').catch(() => []),
          apiCall('GET', '/kitchen/history/').catch(() => []),
          apiCall('GET', '/alerts/alerts/').catch(() => []),
        ])

      const orders = ordersRaw.results || ordersRaw || []
      const kitchenQueue = kitchenRaw || []
      const receipts = receiptsRaw.results || receiptsRaw || []
      const tables = tablesRaw.results || tablesRaw || []
      const kitchenHistory = kitchenHistoryRaw || []
      const alerts = alertsRaw.results || alertsRaw || []

      const orderTime = (o) => new Date(o.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })

      const activeOrders = orders
        .filter((o) => !['served', 'declined', 'cancelled'].includes(o.status))
        .map((o) => ({
          orderId: o.order_id,
          id: o.id,
          itemId: o.menu_item,
          name: o.menu_item_name || '',
          emoji: o.menu_item_emoji || '',
          price: parseFloat(o.menu_item_price || 0),
          table: o.table_number || null,
          side: o.side || 'Plain',
          qty: o.quantity || 1,
          total: parseFloat(o.total || 0),
          source: o.source === 'customer' ? 'online' : 'barni',
          ready: o.status === 'ready',
          status: o.status,
        }))

      const pendingCustomerOrders = orders
        .filter((o) => o.source === 'customer' && o.status === 'pending')
        .map((o) => ({
          qid: o.order_id,
          id: o.id,
          itemId: o.menu_item,
          name: o.menu_item_name || '',
          emoji: o.menu_item_emoji || '',
          price: parseFloat(o.menu_item_price || 0),
          side: o.side || 'Plain',
          qty: o.quantity || 1,
          total: parseFloat(o.total || 0),
        }))

      const kitchenItems = kitchenQueue.map((k) => ({
        kitchenId: k.id,
        orderId: k.order?.order_id || '',
        orderUuid: k.order?.id || '',
        itemId: k.order?.menu_item || '',
        name: k.menu_item_name || '',
        emoji: k.menu_item_emoji || '',
        qty: k.order?.quantity || 1,
        side: k.order?.side || 'Plain',
        source: k.order?.source || 'barni',
        ingredients: k.menu_item_ingredients || [],
        status: k.status,
      }))

      const waiterReports = orders
        .filter((o) => ['served', 'ready'].includes(o.status))
        .map((o) => ({
          orderId: o.order_id,
          name: o.menu_item_name || '',
          table: o.source === 'customer' ? 'Online' : (o.table_number ? `Table ${o.table_number}` : '—'),
          orderType: o.source === 'customer' ? 'Online' : 'At Barni',
          payment: o.payment_method || '',
          price: parseFloat(o.menu_item_price || 0),
          qty: o.quantity || 1,
          side: o.side || 'Plain',
          time: orderTime(o),
          status: o.status,
          declined: o.status === 'declined',
        }))

      const kitchenReports = kitchenHistory
        .map((k) => ({
          orderId: k.order?.order_id || '',
          name: k.menu_item_name || '',
          qty: k.order?.quantity || 1,
          side: k.order?.side || 'Plain',
          time: new Date(k.completed_at || k.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }),
        }))

      const tableList = tables.map((t) => t.number)

      return {
        orders: activeOrders,
        queue: pendingCustomerOrders,
        kitchenQueue: kitchenItems,
        waiterReports,
        kitchenReports,
        receipts: receipts.map((r) => ({
          id: r.receipt_number,
          orderId: r.order,
          waiter: r.waiter || '',
          table: r.table_label || '',
          item: r.item_label || '',
          qty: r.quantity || 1,
          total: parseFloat(r.total || 0),
          payment: r.payment_method || '',
          time: new Date(r.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }),
          qrData: r.qr_data || '',
        })),
        issues: alerts.map((a) => ({
          id: a.id,
          author: a.author_name || a.author || '',
          role: (a.author_name || '').toLowerCase().includes('kitchen') ? 'kitchen' : 'waiter',
          kind: a.title || a.alert_type || '',
          detail: a.detail || '',
          time: new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }),
          status: a.status,
          response: a.response || null,
        })),
        tables: tableList,
      }
    } catch {
      return {
        orders: [],
        queue: [],
        kitchenQueue: [],
        waiterReports: [],
        kitchenReports: [],
        receipts: [],
        issues: [],
        tables: Array.from({ length: 15 }, (_, i) => i + 1),
      }
    }
  },

  /* ---------------------------- waiter orders --------------------------- */

  async placeOrder(item, { table, qty, side }) {
    const data = await apiCall('POST', '/orders/place/', {
      menu_item_id: item.id || item.itemId,
      table_id: table,
      side: side || 'Plain',
      quantity: qty || 1,
      source: 'barni',
    })
    return {
      orderId: data.order_id,
      id: data.id,
      itemId: data.menu_item,
      name: data.menu_item_name || item.name,
      emoji: data.menu_item_emoji || item.emoji,
      price: parseFloat(data.menu_item_price || item.price),
      table: data.table_number || table,
      side: data.side || side,
      qty: data.quantity || qty,
      total: parseFloat(data.total || 0),
      source: 'barni',
      ready: false,
      status: data.status,
    }
  },

  async cancelOrder(orderId) {
    const orders = await apiCall('GET', '/orders/orders/')
    const list = orders.results || orders || []
    const order = list.find((o) => o.order_id === orderId || o.id === orderId)
    if (!order) throw new Error('Order not found')
    await apiCall('POST', `/orders/${order.id}/cancel/`)
    return { ok: true }
  },

  /* ---------------------------- online queue ---------------------------- */

  async simulateOnlineOrder(item) {
    return { qid: '#' + Math.random().toString(36).slice(2, 6), item }
  },

  async declineOnline(qid) {
    const orders = await apiCall('GET', '/orders/orders/')
    const list = orders.results || orders || []
    const order = list.find((o) => o.order_id === qid || o.id === qid)
    if (!order) throw new Error('Order not found')
    await apiCall('POST', `/orders/${order.id}/cancel/`)
    return { qid }
  },

  async acceptOnline(qid) {
    const orders = await apiCall('GET', '/orders/orders/?status=pending')
    const list = orders.results || orders || []
    const order = list.find((o) => o.order_id === qid || o.id === qid)
    if (!order) throw new Error('Order not found')
    const data = await apiCall('POST', `/orders/${order.id}/accept/`)
    return {
      orderId: data.order_id,
      id: data.id,
      itemId: data.menu_item,
      name: data.menu_item_name || '',
      emoji: data.menu_item_emoji || '',
      price: parseFloat(data.menu_item_price || 0),
      source: data.source,
      ready: false,
      table: null,
      qty: data.quantity || 1,
      side: data.side || 'Plain',
      total: parseFloat(data.total || 0),
      status: data.status,
    }
  },

  /* ------------------------------ kitchen ------------------------------- */

  async markKitchenDone(kitchenId) {
    await apiCall('POST', `/kitchen/${kitchenId}/status/`, {
      status: 'ready',
    })
    await apiCall('POST', `/kitchen/${kitchenId}/status/`, {
      status: 'done',
    })
    return { ok: true }
  },

  /* ------------------------------ payment ------------------------------- */

  async payOrder(order, { waiter, method, source, itemLabel, qrData }) {
    const orderId = order.id || order.orderId
    const data = await apiCall('POST', `/orders/${orderId}/pay/`, {
      payment_method: method || 'Cash',
      qr_data: qrData || '',
    })
    return {
      id: data.receipt_number || data.id,
      orderId: order.orderId,
      itemId: order.itemId,
      waiter: waiter,
      table: source === 'online' ? 'Online order' : `Table ${order.table}`,
      item: itemLabel || order.name,
      qty: order.qty || 1,
      total: parseFloat(data.total || order.total || 0),
      payment: method,
      time: now(),
      qrData: qrData || null,
    }
  },

  /* ----------------------------- issues --------------------------------- */

  async submitIssue({ author, role, kind, category, item, priority, detail }) {
    await apiCall('POST', '/alerts/alerts/', {
      title: kind || 'Issue',
      alert_type: 'issue',
      detail: detail || '',
    })
    return { ok: true }
  },

  async respondToIssue(id, response) {
    await apiCall('POST', `/alerts/${id}/respond/`, { response })
    return { ok: true }
  },

  async resolveIssue(id, resolvedBy) {
    await apiCall('PATCH', `/alerts/alerts/${id}/`, { status: 'resolved' })
    return { ok: true }
  },

  async startShift(username, tables) {
    return { ok: true, tables }
  },

  /* ----------------------------- history -------------------------------- */

  getHistoryDays() {
    const today = businessDayKey()
    const days = [
      { day: today, label: dayLabel(today), isToday: true },
      ...lastNDays(7)
        .filter((k) => k !== today)
        .map((k) => ({ day: k, label: dayLabel(k), isToday: false })),
    ].reverse()
    return days
  },

  async getHistory(dayKey) {
    const today = businessDayKey()
    const isToday = dayKey === today
    const dateISO = dayKeyToISO(dayKey)

    if (isToday) {
      const [waiterReports, kitchenReports, receiptsRaw] = await Promise.all([
        apiCall('GET', '/reports/waiter/').catch(() => []),
        apiCall('GET', '/reports/kitchen/').catch(() => []),
        apiCall('GET', '/orders/receipts/').catch(() => []),
      ])
      const receipts = (receiptsRaw.results || receiptsRaw || []).map((r) => ({
        item: r.item_label,
        total: parseFloat(r.total || 0),
        payment: r.payment_method,
        waiter: r.waiter || '',
        table: r.table_label || '',
        time: new Date(r.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }),
      }))
      return {
        day: dayKey,
        label: dayLabel(dayKey),
        isToday: true,
        orders: waiterReports || [],
        kitchen: kitchenReports || [],
        receipts,
      }
    }

    const [waiterReports, kitchenReports] = await Promise.all([
      apiCall('GET', `/reports/waiter/?date=${dateISO}`).catch(() => []),
      apiCall('GET', `/reports/kitchen/?date=${dateISO}`).catch(() => []),
    ])
    return {
      day: dayKey,
      label: dayLabel(dayKey),
      isToday: false,
      orders: waiterReports || [],
      kitchen: kitchenReports || [],
      receipts: waiterReports || [],
    }
  },

  /* ---------------------------- customer -------------------------------- */

  async customerPlaceOrder(customerName, item, { side, qty, payment }) {
    const data = await apiCall('POST', '/orders/customer/place/', {
      menu_item_id: item.id,
      side: side || 'Plain',
      quantity: qty || 1,
      payment_method: payment || 'Cash',
    })
    return {
      orderId: data.order_id,
      total: parseFloat(data.total || 0),
      status: data.status,
      time: now(),
    }
  },

  getCustomerOrders(customerName) {
    return []
  },

  /* ---------------------------- menu items ----------------------------- */

  async fetchMenuItems() {
    const data = await apiCall('GET', '/menu/items/')
    const list = data.results || data || []
    return list.filter((i) => i.is_available && i.item_type !== 'side').map((i) => ({
      id: i.id,
      name: i.name,
      emoji: i.emoji || '',
      price: parseFloat(i.price || 0),
      type: i.item_type,
    }))
  },

  async fetchCustomerOrders() {
    const data = await apiCall('GET', '/orders/customer/my-orders/').catch(() => [])
    const list = data.results || data || []
    return list.map((o) => ({
      orderId: o.order_id,
      id: o.id,
      itemId: o.menu_item,
      name: o.menu_item_name || '',
      emoji: o.menu_item_emoji || '',
      price: parseFloat(o.menu_item_price || 0),
      side: o.side || 'Plain',
      qty: o.quantity || 1,
      total: parseFloat(o.total || 0),
      payment: o.payment_method || '',
      status: o.status,
      time: new Date(o.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }),
    }))
  },

  async chapaPay(customerName, orderId, { email, phone, amount }) {
    return {
      success: true,
      txRef: 'CHAPA-' + Math.random().toString(36).slice(2, 10).toUpperCase(),
      amount,
      message: 'Payment successful!',
    }
  },

  async uploadProfilePicture(file) {
    const formData = new FormData()
    formData.append('profile_picture', file)
    const res = await fetch(`${BASE}/auth/upload-picture/`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${getToken()}` },
      body: formData,
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.error || 'Upload failed')
    }
    return await res.json()
  },

  async fetchCurrentUser() {
    return await apiCall('GET', '/auth/me/')
  },
}

/* ------------------------------- utils ---------------------------------- */

function dayKeyToISO(dayKey) {
  if (!dayKey || dayKey.length !== 8) return todayISO()
  return `${dayKey.slice(0, 4)}-${dayKey.slice(4, 6)}-${dayKey.slice(6, 8)}`
}
