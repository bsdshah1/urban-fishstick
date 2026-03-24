import { apiFetch } from './client'
import type { Digest, DigestUpdate, GenerateRequest } from './types'

export const getDigests = () => apiFetch<Digest[]>('/api/digests')
export const getDigest = (id: number) => apiFetch<Digest>(`/api/digests/${id}`)

export const updateDigest = (id: number, data: DigestUpdate) =>
  apiFetch<Digest>(`/api/digests/${id}`, { method: 'PATCH', body: JSON.stringify(data) })

export const approveDigest = (id: number) =>
  apiFetch<Digest>(`/api/digests/${id}/approve`, { method: 'POST' })

export const publishDigest = (id: number) =>
  apiFetch<Digest>(`/api/digests/${id}/publish`, { method: 'POST' })

export const flagDigest = (id: number, note?: string) =>
  apiFetch<Digest>(`/api/digests/${id}/flag`, { method: 'POST', body: JSON.stringify({ note }) })

export const generateDigest = (data: GenerateRequest) =>
  apiFetch<Digest>('/api/generate', { method: 'POST', body: JSON.stringify(data) })
