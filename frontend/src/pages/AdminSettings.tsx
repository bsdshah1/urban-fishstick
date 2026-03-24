import { useEffect, useState } from 'react'
import { getSettings, updateSettings, getUsers, createUser, deactivateUser } from '../api/admin'
import type { Settings, User } from '../api/types'
import { Button } from '../components/shared/Button'
import { Toast } from '../components/shared/Toast'
import styles from './AdminSettings.module.css'

const TERMS = ['autumn', 'spring', 'summer']

export function AdminSettings() {
  const [settings, setSettings] = useState<Settings | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null)

  // New user form
  const [newName, setNewName] = useState('')
  const [newEmail, setNewEmail] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [newRole, setNewRole] = useState<'teacher' | 'parent' | 'admin'>('teacher')
  const [addingUser, setAddingUser] = useState(false)
  const [showAddUser, setShowAddUser] = useState(false)

  useEffect(() => {
    Promise.all([getSettings(), getUsers()])
      .then(([s, u]) => { setSettings(s); setUsers(u) })
      .finally(() => setLoading(false))
  }, [])

  const handleSaveSettings = async () => {
    if (!settings) return
    setSaving(true)
    try {
      const updated = await updateSettings({
        current_term: settings.current_term,
        current_week: settings.current_week,
      })
      setSettings(updated)
      setToast({ msg: 'Settings saved.', type: 'success' })
    } catch (e: unknown) {
      setToast({ msg: e instanceof Error ? e.message : 'Failed to save', type: 'error' })
    } finally { setSaving(false) }
  }

  const handleAddUser = async () => {
    if (!newEmail || !newPassword || !newName) return
    setAddingUser(true)
    try {
      const user = await createUser({ email: newEmail, password: newPassword, name: newName, role: newRole })
      setUsers(u => [...u, user])
      setNewEmail(''); setNewPassword(''); setNewName('')
      setShowAddUser(false)
      setToast({ msg: `${user.name} added.`, type: 'success' })
    } catch (e: unknown) {
      setToast({ msg: e instanceof Error ? e.message : 'Failed', type: 'error' })
    } finally { setAddingUser(false) }
  }

  const handleDeactivate = async (id: number, name: string) => {
    if (!confirm(`Deactivate ${name}? They will no longer be able to sign in.`)) return
    try {
      await deactivateUser(id)
      setUsers(u => u.map(usr => usr.id === id ? { ...usr, is_active: false } : usr))
      setToast({ msg: `${name} deactivated.`, type: 'success' })
    } catch { setToast({ msg: 'Failed', type: 'error' }) }
  }

  if (loading) return <div className={styles.loading}>Loading settings…</div>

  return (
    <div className={styles.page}>
      {toast && <Toast message={toast.msg} type={toast.type} onDismiss={() => setToast(null)} />}
      <div className={styles.container}>
        <h1 className={styles.title}>School Settings</h1>

        {settings && (
          <section className={styles.panel}>
            <h2 className={styles.panelTitle}>Current Period</h2>
            <p className={styles.panelDesc}>Controls which term and week are displayed to parents.</p>
            <div className={styles.formRow}>
              <div className={styles.field}>
                <label className={styles.label}>Current term</label>
                <select
                  className={styles.select}
                  value={settings.current_term}
                  onChange={e => setSettings({ ...settings, current_term: e.target.value })}
                >
                  {TERMS.map(t => (
                    <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)} Term</option>
                  ))}
                </select>
              </div>
              <div className={styles.field}>
                <label className={styles.label}>Current week</label>
                <input
                  type="number"
                  className={styles.input}
                  min={1}
                  max={14}
                  value={settings.current_week}
                  onChange={e => setSettings({ ...settings, current_week: parseInt(e.target.value, 10) || 1 })}
                />
              </div>
            </div>
            <Button variant="primary" onClick={handleSaveSettings} loading={saving}>Save changes</Button>
          </section>
        )}

        <section className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <h2 className={styles.panelTitle}>Teacher Accounts</h2>
              <p className={styles.panelDesc}>{users.filter(u => u.is_active).length} active users</p>
            </div>
            <Button variant="secondary" onClick={() => setShowAddUser(v => !v)}>+ Add user</Button>
          </div>

          {showAddUser && (
            <div className={styles.addUserForm}>
              <div className={styles.formRow}>
                <div className={styles.field}>
                  <label className={styles.label}>Name</label>
                  <input className={styles.input} value={newName} onChange={e => setNewName(e.target.value)} placeholder="Full name" />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Email</label>
                  <input className={styles.input} type="email" value={newEmail} onChange={e => setNewEmail(e.target.value)} placeholder="name@beaumont.sch.uk" />
                </div>
              </div>
              <div className={styles.formRow}>
                <div className={styles.field}>
                  <label className={styles.label}>Temporary password</label>
                  <input className={styles.input} type="password" value={newPassword} onChange={e => setNewPassword(e.target.value)} />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Role</label>
                  <select className={styles.select} value={newRole} onChange={e => setNewRole(e.target.value as typeof newRole)}>
                    <option value="teacher">Teacher</option>
                    <option value="admin">Admin</option>
                    <option value="parent">Parent</option>
                  </select>
                </div>
              </div>
              <div className={styles.addActions}>
                <Button variant="primary" onClick={handleAddUser} loading={addingUser}>Add user</Button>
                <Button variant="ghost" onClick={() => setShowAddUser(false)}>Cancel</Button>
              </div>
            </div>
          )}

          <table className={styles.table}>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id} className={!user.is_active ? styles.inactive : ''}>
                  <td>{user.name}</td>
                  <td className={styles.email}>{user.email}</td>
                  <td className={styles.role}>{user.role}</td>
                  <td>{user.is_active ? <span className={styles.active}>Active</span> : <span className={styles.deactivated}>Deactivated</span>}</td>
                  <td>
                    {user.is_active && (
                      <button className={styles.deactivateBtn} onClick={() => handleDeactivate(user.id, user.name)}>
                        Deactivate
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  )
}
