import { useState } from 'react'
import Modal from '../components/Modal'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { api } from '../services/api'

const ROLES = [
  { id: 'admin', icon: '👑', label: 'Admin' },
  { id: 'waiter', icon: '🧑‍🍳', label: 'Waiter' },
  { id: 'customer', icon: '📱', label: 'Customer' },
  { id: 'kitchen', icon: '🍳', label: 'Kitchen' },
]

const REGISTER_ROLES = [
  { id: 'waiter', icon: '🧑‍🍳', label: 'Waiter' },
  { id: 'customer', icon: '📱', label: 'Customer' },
  { id: 'kitchen', icon: '🍳', label: 'Kitchen' },
]

export default function LoginPage() {
  const { login, register, resetPassword } = useAuth()
  const { showToast } = useToast()
  const [role, setRole] = useState('admin')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const [registerOpen, setRegisterOpen] = useState(false)
  const [forgotOpen, setForgotOpen] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    if (!username.trim()) return setError('Username is required.')
    if (!password) return setError('Password is required.')
    setBusy(true)
    try {
      await login(username, password, role)
      if (role !== 'customer') {
        showToast(`Welcome, ${username}`, 'success')
      }
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  const isCustomer = role === 'customer'

  return (
    <div className="app-screen center-screen show">
      <form className="login-card" onSubmit={submit}>
        <div className="login-card-head">
          <div className="login-icon-badge">
            <svg width="24" height="24" viewBox="0 0 44 44" aria-hidden="true">
              <path d="M9 16 h20 v8 a10 10 0 0 1 -20 0 z" fill="#181008" />
              <rect x="8" y="14" width="22" height="3.5" rx="1.75" fill="#181008" />
              <path d="M29 19 q6 -0.5 6 4.5 t-6 5" fill="none" stroke="#181008" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </div>
          <div className="login-title">BARNI COFFEE</div>
        </div>
        <div className="login-tagline">
          {isCustomer ? 'Order your favorite food' : 'Enterprise Console'}
        </div>

        <div className="role-tabs">
          {ROLES.map((r) => (
            <div
              key={r.id}
              className={`role-tab ${role === r.id ? 'active' : ''}`}
              onClick={() => {
                setRole(r.id)
                setError('')
                setUsername('')
                setPassword('')
              }}
            >
              <span className="rt-icon">{r.icon}</span>
              <span className="rt-label">{r.label}</span>
            </div>
          ))}
        </div>

        <label className="field-label">Username</label>
        <input
          className="auth-input"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
        />
        <label className="field-label">Password</label>
        <input
          className="auth-input"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
        />

        <div className="form-error">{error}</div>
        <button className="modal-primary-btn" type="submit" disabled={busy || !username || !password}>
          {busy ? 'Signing in…' : isCustomer ? 'Browse Menu →' : 'Sign in →'}
        </button>

        <div className="modal-links-row">
          <span className="modal-link" onClick={() => setRegisterOpen(true)}>
            Register
          </span>
          <span>·</span>
          <span className="modal-link" onClick={() => setForgotOpen(true)}>
            Forgot password
          </span>
        </div>
      </form>

      <RegisterModal
        open={registerOpen}
        onClose={() => setRegisterOpen(false)}
        onDone={(uname) => {
          setRegisterOpen(false)
          setRole(isCustomer ? 'customer' : role)
          setUsername(uname)
          setPassword('')
        }}
        register={register}
        showToast={showToast}
        isCustomer={isCustomer}
        staffRole={isCustomer ? 'customer' : role}
      />
      <ForgotModal
        open={forgotOpen}
        onClose={() => setForgotOpen(false)}
        onDone={(uname) => {
          setForgotOpen(false)
          setRole('waiter')
          setUsername(uname)
          setPassword('')
        }}
        resetPassword={resetPassword}
        showToast={showToast}
      />
    </div>
  )
}

function RegisterModal({ open, onClose, onDone, register, showToast, isCustomer, staffRole }) {
  const [regRole, setRegRole] = useState(staffRole || 'waiter')
  const [form, setForm] = useState({ fullName: '', fatherName: '', phone: '', email: '', username: '', password: '', confirm: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')

    if (!form.fullName.trim()) return setError('Full name is required.')
    if (!form.phone.trim()) return setError('Phone number is required.')
    if (!/^\d{10}$/.test(form.phone.trim())) return setError('Phone must be exactly 10 digits.')
    if (!form.username.trim()) return setError('Username is required.')
    if (!form.password) return setError('Password is required.')
    if (form.password.length < 4) return setError('Password must be at least 4 characters.')
    if (form.password !== form.confirm) return setError('Passwords do not match.')

    const role = isCustomer ? 'Customer' : regRole.charAt(0).toUpperCase() + regRole.slice(1)

    setBusy(true)
    try {
      await api.register({
        username: form.username,
        password: form.password,
        role,
        full_name: form.fullName,
        father_name: form.fatherName,
        phone: form.phone,
        email: form.email,
      })
      showToast('Registered - please sign in', 'success')
      onDone(form.username)
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose} title={isCustomer ? 'CREATE ACCOUNT' : 'STAFF REGISTRATION'} subtitle="Create your account to begin">
      <form onSubmit={submit}>
        {!isCustomer && (
          <div className="grid-3" style={{ marginBottom: 10 }}>
            {REGISTER_ROLES.map((r) => (
              <div key={r.id} className={`pick-box ${regRole === r.id ? 'selected' : ''}`} onClick={() => setRegRole(r.id)}>
                <span>{r.icon}</span> {r.label}
              </div>
            ))}
          </div>
        )}
        <input className="auth-input" placeholder="Full name" value={form.fullName} onChange={set('fullName')} />
        {!isCustomer && (
          <input className="auth-input" placeholder="Father's name" value={form.fatherName} onChange={set('fatherName')} />
        )}
        <input className="auth-input" placeholder="Phone number (10 digits)" inputMode="numeric" pattern="\d*" value={form.phone}
          onKeyDown={(e) => { if (/[a-zA-Z]/.test(e.key)) e.preventDefault() }}
          onInput={(e) => { e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 10) }}
          onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value.replace(/[^0-9]/g, '').slice(0, 10) }))} />
        <input className="auth-input" type="email" placeholder="Email (optional)" value={form.email} onChange={set('email')} />
        <input className="auth-input" placeholder="Username" value={form.username} onChange={set('username')} />
        <input className="auth-input" type="password" placeholder="Password" value={form.password} onChange={set('password')} />
        <input className="auth-input" type="password" placeholder="Confirm password" value={form.confirm} onChange={set('confirm')} />
        <div className="form-error">{error}</div>
        <button className="modal-primary-btn" type="submit" disabled={busy}>
          {busy ? 'Creating…' : 'Register'}
        </button>
      </form>
    </Modal>
  )
}

function ForgotModal({ open, onClose, onDone, resetPassword, showToast }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if (!username.trim()) return setError('Username is required.')
    if (!password) return setError('Password is required.')
    if (password !== confirm) return setError('Passwords do not match.')
    setBusy(true)
    setError('')
    try {
      await resetPassword({ username, password })
      showToast('Password updated - please sign in', 'success')
      onDone(username)
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="RESET PASSWORD" subtitle="Enter your username and a new password">
      <form onSubmit={submit}>
        <input className="auth-input" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input className="auth-input" type="password" placeholder="New password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <input className="auth-input" type="password" placeholder="Confirm new password" value={confirm} onChange={(e) => setConfirm(e.target.value)} />
        <div className="form-error">{error}</div>
        <button className="modal-primary-btn" type="submit" disabled={busy}>
          {busy ? 'Resetting…' : 'Reset Password'}
        </button>
      </form>
    </Modal>
  )
}
