import { useState, useRef } from 'react'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { api } from '../services/api'
import { PAY_ACCOUNTS } from '../data/menu'

const CONTACT_INFO = {
  phone: '+251 911 000 000',
  email: 'info@barnicoffee.com',
  location: 'Addis Ababa, Bole Road',
  adminPhone: '+251 911 111 111',
  adminEmail: 'admin@barnicoffee.com',
}

const ROLE_LABEL = { waiter: 'Waiter', kitchen: 'Kitchen', admin: 'Admin', customer: 'Customer' }

export default function ProfilePage({ onNavigate }) {
  const { user, updateUser } = useAuth()
  const { showToast } = useToast()
  const fileInputRef = useRef(null)
  const [uploading, setUploading] = useState(false)

  const role = user?.role || 'customer'

  const handleUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (file.size > 5 * 1024 * 1024) {
      showToast('Image must be under 5MB', 'error')
      return
    }
    setUploading(true)
    try {
      const data = await api.uploadProfilePicture(file)
      if (updateUser) updateUser({ profilePicture: data.profile_picture })
      showToast('Profile picture updated!', 'success')
    } catch (err) {
      showToast(err.message || 'Upload failed', 'error')
    }
    setUploading(false)
  }

  const initials = (user?.fullName || user?.username || '?').charAt(0).toUpperCase()
  const picUrl = user?.profilePicture

  return (
    <div className="board single">
      <div className="profile-page">
        <div className="profile-header">
          <div
            className="profile-avatar"
            onClick={() => fileInputRef.current?.click()}
            style={{ cursor: 'pointer', position: 'relative' }}
          >
            {picUrl ? (
              <img src={picUrl} alt="avatar" style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }} />
            ) : (
              <span style={{ fontSize: 36, lineHeight: '64px' }}>{initials}</span>
            )}
            <div style={{ position: 'absolute', bottom: 0, right: 0, background: '#f5d020', borderRadius: '50%', width: 22, height: 22, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, color: '#000', border: '2px solid #111' }}>
              {uploading ? '...' : '+'}
            </div>
          </div>
          <input ref={fileInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handleUpload} />
          <div className="profile-name">{user?.fullName || user?.username}</div>
          <div className="profile-role">{ROLE_LABEL[role] || role}</div>
        </div>

        <div className="profile-section">
          <div className="panel-title">Account Information</div>
          <div className="profile-info-row"><span>Full Name</span><span>{user?.fullName || user?.username}</span></div>
          <div className="profile-info-row"><span>Username</span><span>{user?.username}</span></div>
          <div className="profile-info-row"><span>Role</span><span>{ROLE_LABEL[role]}</span></div>
          {user?.tables && user.tables.length > 0 && (
            <div className="profile-info-row"><span>Assigned Tables</span><span>{user.tables.join(', ')}</span></div>
          )}
        </div>

        {role === 'customer' && (
          <>
            <div className="profile-section">
              <div className="panel-title">Contact Admin</div>
              <div className="profile-contact-grid">
                <div className="profile-contact-card">
                  <div className="profile-contact-icon">📞</div>
                  <div className="profile-contact-label">Phone</div>
                  <div className="profile-contact-value">{CONTACT_INFO.adminPhone}</div>
                </div>
                <div className="profile-contact-card">
                  <div className="profile-contact-icon">✉️</div>
                  <div className="profile-contact-label">Email</div>
                  <div className="profile-contact-value">{CONTACT_INFO.adminEmail}</div>
                </div>
                <div className="profile-contact-card">
                  <div className="profile-contact-icon">📍</div>
                  <div className="profile-contact-label">Location</div>
                  <div className="profile-contact-value">{CONTACT_INFO.location}</div>
                </div>
                <div className="profile-contact-card">
                  <div className="profile-contact-icon">💬</div>
                  <div className="profile-contact-label">Message</div>
                  <div className="profile-contact-value">WhatsApp / Telegram</div>
                </div>
              </div>
            </div>

            <div className="profile-section">
              <div className="panel-title">Restaurant Payment Accounts</div>
              <div className="profile-accounts">
                {Object.entries(PAY_ACCOUNTS).map(([key, acc]) => (
                  <div className="profile-account-card" key={key}>
                    <div className="profile-account-bank">{acc.bank}</div>
                    <div className="profile-account-number">{acc.accountNumber}</div>
                    <div className="profile-account-name">Name: {acc.accountName}</div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {role !== 'customer' && (
          <div className="profile-section">
            <div className="panel-title">Contact Admin</div>
            <div className="profile-contact-grid">
              <div className="profile-contact-card">
                <div className="profile-contact-icon">📞</div>
                <div className="profile-contact-label">Phone</div>
                <div className="profile-contact-value">{CONTACT_INFO.adminPhone}</div>
              </div>
              <div className="profile-contact-card">
                <div className="profile-contact-icon">✉️</div>
                <div className="profile-contact-label">Email</div>
                <div className="profile-contact-value">{CONTACT_INFO.adminEmail}</div>
              </div>
              <div className="profile-contact-card">
                <div className="profile-contact-icon">📍</div>
                <div className="profile-contact-label">Location</div>
                <div className="profile-contact-value">{CONTACT_INFO.location}</div>
              </div>
              <div className="profile-contact-card">
                <div className="profile-contact-icon">💬</div>
                <div className="profile-contact-label">Message</div>
                <div className="profile-contact-value">WhatsApp / Telegram</div>
              </div>
            </div>
          </div>
        )}

        <div className="profile-section">
          <div className="panel-title">App Info</div>
          <div className="profile-info-row"><span>Version</span><span>1.0.0</span></div>
          <div className="profile-info-row"><span>Platform</span><span>Barni Coffee POS</span></div>
        </div>

        <button className="modal-primary-btn" onClick={() => onNavigate(role === 'customer' ? 'menu' : 'menu')}>
          Back to Menu
        </button>
      </div>
    </div>
  )
}
