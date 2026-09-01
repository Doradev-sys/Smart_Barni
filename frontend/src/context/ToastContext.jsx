import { createContext, useCallback, useContext, useRef, useState } from 'react'

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toast, setToast] = useState(null)
  const timer = useRef(null)

  const showToast = useCallback((message, kind = 'info') => {
    setToast({ message, kind, key: Date.now() })
    clearTimeout(timer.current)
    timer.current = setTimeout(() => setToast(null), 2600)
  }, [])

  return (
    <ToastContext.Provider value={{ toast, showToast }}>
      {children}
      <div className={`toast toast-${toast?.kind || 'info'} ${toast ? 'show' : ''}`} key={toast?.key}>
        {toast?.message}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  return useContext(ToastContext)
}
