import React, { useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Outlet, Route, Routes, useLocation } from 'react-router-dom'
import type { User } from './api/types'
import { AppShell } from './components/shared/AppShell'
import { Login } from './pages/Login'
import { ParentDigest } from './pages/ParentDigest'
import { TeacherDashboard } from './pages/TeacherDashboard'
import { ContentHistory } from './pages/ContentHistory'
import { AdminSettings } from './pages/AdminSettings'

function getStoredUser(): User | null {
  const raw = localStorage.getItem('bm_user')
  if (!raw) return null
  try { return JSON.parse(raw) as User } catch { return null }
}

function RequireRole({
  user, roles, children,
}: { user: User | null; roles: string[]; children: React.ReactElement }) {
  const location = useLocation()
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />
  if (!roles.includes(user.role)) return <Navigate to="/" replace />
  return children
}

function DefaultRedirect({ user }: { user: User | null }) {
  if (!user) return <Navigate to="/login" replace />
  if (user.role === 'parent') return <Navigate to="/digest" replace />
  if (user.role === 'admin') return <Navigate to="/admin" replace />
  return <Navigate to="/teacher" replace />
}

function AppLayout({ user }: { user: User | null }) {
  return (
    <AppShell user={user}>
      <Outlet />
    </AppShell>
  )
}

export default function App() {
  const [user, setUser] = useState<User | null>(getStoredUser)

  useEffect(() => {
    const onStorage = () => setUser(getStoredUser())
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login setUser={setUser} />} />

        <Route element={<AppLayout user={user} />}>
          <Route index element={<DefaultRedirect user={user} />} />

          <Route
            path="digest"
            element={
              <RequireRole user={user} roles={['parent', 'teacher', 'admin']}>
                <ParentDigest user={user!} />
              </RequireRole>
            }
          />

          <Route
            path="teacher"
            element={
              <RequireRole user={user} roles={['teacher', 'admin']}>
                <TeacherDashboard user={user!} />
              </RequireRole>
            }
          />

          <Route
            path="history"
            element={
              <RequireRole user={user} roles={['teacher', 'admin']}>
                <ContentHistory />
              </RequireRole>
            }
          />

          <Route
            path="admin"
            element={
              <RequireRole user={user} roles={['admin']}>
                <AdminSettings />
              </RequireRole>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
