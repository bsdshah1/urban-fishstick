import { useEffect, useState } from 'react'
import { getDigests, publishDigest } from '../api/digests'
import type { Digest } from '../api/types'
import { StatusBadge } from '../components/shared/StatusBadge'
import { Toast } from '../components/shared/Toast'
import styles from './ContentHistory.module.css'

const TERM_LABELS: Record<string, string> = {
  autumn: 'Autumn Term', spring: 'Spring Term', summer: 'Summer Term',
}

export function ContentHistory() {
  const [digests, setDigests] = useState<Digest[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [expanded, setExpanded] = useState<number | null>(null)
  const [toast, setToast] = useState<string | null>(null)

  useEffect(() => {
    getDigests().then(setDigests).finally(() => setLoading(false))
  }, [])

  const filtered = digests.filter(d => {
    const matchesSearch = d.unit_title.toLowerCase().includes(search.toLowerCase())
    const matchesStatus = statusFilter === 'all' || d.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const handleRepublish = async (id: number) => {
    try {
      const updated = await publishDigest(id)
      setDigests(ds => ds.map(d => d.id === id ? updated : d))
      setToast('Digest re-published.')
    } catch { setToast('Failed to re-publish.') }
  }

  if (loading) return <div className={styles.loading}>Loading history…</div>

  return (
    <div className={styles.page}>
      {toast && <Toast message={toast} onDismiss={() => setToast(null)} />}
      <div className={styles.container}>
        <h1 className={styles.title}>Content History</h1>
        <p className={styles.subtitle}>{digests.length} digest{digests.length !== 1 ? 's' : ''} total</p>

        <div className={styles.toolbar}>
          <input
            className={styles.search}
            type="search"
            placeholder="Search by unit title…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            aria-label="Search digests"
          />
          <select
            className={styles.filter}
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            aria-label="Filter by status"
          >
            <option value="all">All statuses</option>
            <option value="draft">Draft</option>
            <option value="approved">Approved</option>
            <option value="published">Published</option>
            <option value="flagged">Flagged</option>
          </select>
        </div>

        {filtered.length === 0 ? (
          <p className={styles.empty}>No digests match your search.</p>
        ) : (
          <div className={styles.list}>
            {filtered.map(digest => (
              <div key={digest.id} className={styles.row}>
                <div
                  className={styles.rowHeader}
                  onClick={() => setExpanded(expanded === digest.id ? null : digest.id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={e => e.key === 'Enter' && setExpanded(expanded === digest.id ? null : digest.id)}
                >
                  <div className={styles.rowInfo}>
                    <span className={styles.rowMeta}>{TERM_LABELS[digest.term]} · Week {digest.week_number}</span>
                    <span className={styles.rowTitle}>{digest.unit_title}</span>
                  </div>
                  <div className={styles.rowRight}>
                    <StatusBadge status={digest.status} />
                    {digest.updated_at && (
                      <span className={styles.rowDate}>
                        {new Date(digest.updated_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
                      </span>
                    )}
                    {digest.status === 'published' && (
                      <button
                        className={styles.republishBtn}
                        onClick={e => { e.stopPropagation(); handleRepublish(digest.id) }}
                        type="button"
                      >
                        Re-publish
                      </button>
                    )}
                  </div>
                </div>

                {expanded === digest.id && (
                  <div className={styles.preview}>
                    <h3 className={styles.previewHeading}>Plain English</h3>
                    <p>{digest.plain_english}</p>
                    {digest.teacher_note && (
                      <>
                        <h3 className={styles.previewHeading}>Teacher Note</h3>
                        <p>{digest.teacher_note}</p>
                      </>
                    )}
                    {digest.approved_at && (
                      <p className={styles.auditLine}>
                        Approved {new Date(digest.approved_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })}
                      </p>
                    )}
                    {digest.published_at && (
                      <p className={styles.auditLine}>
                        Published {new Date(digest.published_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
