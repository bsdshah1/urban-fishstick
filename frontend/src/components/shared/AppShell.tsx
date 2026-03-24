import type { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import type { User } from '../../api/types'
import { clearToken } from '../../api/client'
import styles from './AppShell.module.css'

interface Props {
  user: User | null
  children: ReactNode
}

export function AppShell({ user, children }: Props) {
  const location = useLocation()

  const handleLogout = () => {
    clearToken()
    window.location.href = '/login'
  }

  const navLinks = user?.role === 'parent'
    ? [{ to: '/digest', label: 'This Week' }]
    : user?.role === 'teacher'
    ? [
        { to: '/teacher', label: 'Review' },
        { to: '/history', label: 'History' },
      ]
    : user?.role === 'admin'
    ? [
        { to: '/teacher', label: 'Review' },
        { to: '/history', label: 'History' },
        { to: '/admin', label: 'Settings' },
      ]
    : []

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <div className={styles.wordmark}>
            <Link to="/" className={styles.wordmarkLink}>
              <span className={styles.wordmarkSchool}>Beaumont</span>
              <span className={styles.wordmarkProduct}>Maths</span>
            </Link>
          </div>
          <nav className={styles.nav} aria-label="Main navigation">
            {navLinks.map(link => (
              <Link
                key={link.to}
                to={link.to}
                className={`${styles.navLink} ${location.pathname.startsWith(link.to) ? styles.active : ''}`}
              >
                {link.label}
              </Link>
            ))}
          </nav>
          {user && (
            <div className={styles.userArea}>
              <span className={styles.userName}>{user.name}</span>
              <button className={styles.logoutBtn} onClick={handleLogout} type="button">
                Sign out
              </button>
            </div>
          )}
        </div>
      </header>
      <main className={styles.main}>{children}</main>
    </div>
  )
}
