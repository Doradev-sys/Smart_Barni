import { createContext, useContext, useState } from 'react'
import { api } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  const login = async (username, password, role) => {
    const u = await api.login({ username, password, role })
    if (role === 'customer') {
      setUser({ ...u, step: 'app' })
    } else if (u.role === 'waiter') {
      setUser({ ...u, step: 'tables' })
    } else {
      setUser({ ...u, step: 'app' })
    }
    return u
  }

  const register = (payload) => api.register(payload)
  const resetPassword = (payload) => api.resetPassword(payload)

  const startShift = async (tables) => {
    await api.startShift(user.username, tables)
    setUser((u) => ({ ...u, tables, step: 'app' }))
  }

  const updateUser = (patch) => setUser((u) => ({ ...u, ...patch }))

  const logout = () => setUser(null)

  return (
    <AuthContext.Provider
      value={{ user, login, register, resetPassword, startShift, updateUser, logout }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
