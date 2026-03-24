import { apiFetch } from './client'
import type { User } from './types'

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export const login = (email: string, password: string) =>
  apiFetch<LoginResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })

export const me = () => apiFetch<User>('/api/auth/me')
