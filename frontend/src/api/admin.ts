import { apiFetch } from './client'
import type { Settings, User } from './types'

export const getSettings = () => apiFetch<Settings>('/api/admin/settings')
export const updateSettings = (data: Partial<Settings>) =>
  apiFetch<Settings>('/api/admin/settings', { method: 'PATCH', body: JSON.stringify(data) })

export const getUsers = () => apiFetch<User[]>('/api/admin/users')
export const createUser = (data: { email: string; password: string; name: string; role: string }) =>
  apiFetch<User>('/api/admin/users', { method: 'POST', body: JSON.stringify(data) })
export const deactivateUser = (id: number) =>
  apiFetch<void>(`/api/admin/users/${id}`, { method: 'DELETE' })
