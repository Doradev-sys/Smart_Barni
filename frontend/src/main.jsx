import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { AuthProvider } from './context/AuthContext'
import { AppDataProvider } from './context/AppDataContext'
import { ToastProvider } from './context/ToastContext'
import './styles/global.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ToastProvider>
      <AuthProvider>
        <AppDataProvider>
          <App />
        </AppDataProvider>
      </AuthProvider>
    </ToastProvider>
  </React.StrictMode>
)
