import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react'
import { api } from '../services/api'

const AppDataContext = createContext(null)

const EMPTY = {
  orders: [],
  queue: [],
  kitchenQueue: [],
  waiterReports: [],
  kitchenReports: [],
  receipts: [],
  issues: [],
  tables: [],
  customerOrders: [],
}

export function AppDataProvider({ children }) {
  const [state, setState] = useState(EMPTY)
  const [loading, setLoading] = useState(true)
  const [menuItems, setMenuItems] = useState([])

  const refresh = useCallback(async () => {
    try {
      const newState = await api.getState()
      setState(newState)
    } catch {
      // keep current state on error
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchMenu = useCallback(async () => {
    try {
      const items = await api.fetchMenuItems()
      setMenuItems(items)
      return items
    } catch {
      return []
    }
  }, [])

  useEffect(() => {
    refresh()
    const timer = setInterval(refresh, 10000)
    return () => clearInterval(timer)
  }, [refresh])

  /* --------------------------- waiter actions --------------------------- */

  const placeOrder = useCallback(
    async (item, { table, qty, side }) => {
      const order = await api.placeOrder(item, { table, qty, side })
      await refresh()
      return order
    },
    [refresh]
  )

  const cancelOrder = useCallback(
    async (orderId) => {
      await api.cancelOrder(orderId)
      await refresh()
    },
    [refresh]
  )

  /* ---------------------------- online queue ---------------------------- */

  const simulateOnline = useCallback(async () => {
    const items = menuItems.length > 0 ? menuItems : await api.fetchMenuItems()
    const item = items.length > 0 ? items[Math.floor(Math.random() * items.length)] : null
    if (!item) return
    await api.simulateOnlineOrder(item)
    await refresh()
  }, [refresh, menuItems])

  const acceptOnline = useCallback(
    async (qid) => {
      const order = await api.acceptOnline(qid)
      await refresh()
      return order
    },
    [refresh]
  )

  const declineOnline = useCallback(
    async (qid) => {
      await api.declineOnline(qid)
      await refresh()
    },
    [refresh]
  )

  /* ------------------------------ kitchen ------------------------------- */

  const markKitchenDone = useCallback(
    async (kitchenId) => {
      await api.markKitchenDone(kitchenId)
      await refresh()
    },
    [refresh]
  )

  /* ------------------------------ payment ------------------------------- */

  const payOrder = useCallback(
    async (order, { waiter, method, itemLabel, qrData }) => {
      const receipt = await api.payOrder(order, {
        waiter,
        method,
        source: order.source,
        itemLabel,
        qrData: qrData || null,
      })
      await refresh()
      return receipt
    },
    [refresh]
  )

  /* ------------------------------ issues -------------------------------- */

  const submitIssue = useCallback(
    async (payload) => {
      await api.submitIssue(payload)
      await refresh()
    },
    [refresh]
  )

  const respondToIssue = useCallback(
    async (id, response) => {
      await api.respondToIssue(id, response)
      await refresh()
    },
    [refresh]
  )

  const resolveIssue = useCallback(
    async (id, resolvedBy) => {
      await api.resolveIssue(id, resolvedBy)
      await refresh()
    },
    [refresh]
  )

  const getHistoryDays = useCallback(() => api.getHistoryDays(), [])
  const getHistory = useCallback((dayKey) => api.getHistory(dayKey), [])

  /* ------------------------------ customer ------------------------------ */

  const customerPlaceOrder = useCallback(
    async (customerName, item, opts) => {
      const result = await api.customerPlaceOrder(customerName, item, opts)
      await refresh()
      return result
    },
    [refresh]
  )

  const getCustomerOrders = useCallback((customerName) => {
    return api.getCustomerOrders(customerName)
  }, [])

  const fetchCustomerOrders = useCallback(async () => {
    return await api.fetchCustomerOrders()
  }, [])

  const chapaPay = useCallback(
    async (customerName, orderId, details) => {
      const result = await api.chapaPay(customerName, orderId, details)
      await refresh()
      return result
    },
    [refresh]
  )

  return (
    <AppDataContext.Provider
      value={{
        ...state,
        loading,
        menuItems,
        refresh,
        fetchMenu,
        placeOrder,
        cancelOrder,
        simulateOnline,
        acceptOnline,
        declineOnline,
        markKitchenDone,
        payOrder,
        submitIssue,
        respondToIssue,
        resolveIssue,
        getHistoryDays,
        getHistory,
        customerPlaceOrder,
        getCustomerOrders,
        fetchCustomerOrders,
        chapaPay,
      }}
    >
      {children}
    </AppDataContext.Provider>
  )
}

export function useAppData() {
  return useContext(AppDataContext)
}
