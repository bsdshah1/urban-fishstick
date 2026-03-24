import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mockLogin = vi.fn()

vi.mock('./api/auth', () => ({
  login: (...args: unknown[]) => mockLogin(...args),
}))

vi.mock('./pages/TeacherDashboard', () => ({
  TeacherDashboard: () => <div>Teacher Dashboard</div>,
}))

vi.mock('./pages/ParentDigest', () => ({
  ParentDigest: () => <div>Parent Digest</div>,
}))

vi.mock('./pages/ContentHistory', () => ({
  ContentHistory: () => <div>Content History</div>,
}))

vi.mock('./pages/AdminSettings', () => ({
  AdminSettings: () => <div>Admin Settings</div>,
}))

import App from './App'

function renderAt(path: string) {
  window.history.pushState({}, '', path)
  return render(<App />)
}

describe('App auth state sync', () => {
  beforeEach(() => {
    localStorage.clear()
    mockLogin.mockReset()
  })

  it('navigates to /teacher immediately after successful teacher login', async () => {
    mockLogin.mockResolvedValue({
      access_token: 'token',
      token_type: 'bearer',
      user: {
        id: 1,
        email: 'teacher@school.test',
        name: 'Teacher User',
        role: 'teacher',
        is_active: true,
        created_at: '2026-01-01T00:00:00Z',
      },
    })

    renderAt('/login')

    fireEvent.change(screen.getByLabelText(/email address/i), { target: { value: 'teacher@school.test' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } })
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(screen.getByText('Teacher Dashboard')).toBeInTheDocument()
    })
    expect(window.location.pathname).toBe('/teacher')
    expect(screen.queryByRole('button', { name: /sign in/i })).not.toBeInTheDocument()
  })

  it('navigates to /digest immediately after successful parent login', async () => {
    mockLogin.mockResolvedValue({
      access_token: 'token',
      token_type: 'bearer',
      user: {
        id: 2,
        email: 'parent@school.test',
        name: 'Parent User',
        role: 'parent',
        is_active: true,
        created_at: '2026-01-01T00:00:00Z',
      },
    })

    renderAt('/login')

    fireEvent.change(screen.getByLabelText(/email address/i), { target: { value: 'parent@school.test' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } })
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(screen.getByText('Parent Digest')).toBeInTheDocument()
    })
    expect(window.location.pathname).toBe('/digest')
    expect(screen.queryByRole('button', { name: /sign in/i })).not.toBeInTheDocument()
  })
})
