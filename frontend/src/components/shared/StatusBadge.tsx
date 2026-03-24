import type { DigestStatus } from '../../api/types'
import styles from './StatusBadge.module.css'

const LABELS: Record<DigestStatus, string> = {
  draft: 'Draft',
  approved: 'Approved',
  published: 'Published',
  flagged: 'Flagged',
}

export function StatusBadge({ status }: { status: DigestStatus }) {
  return (
    <span className={`${styles.badge} ${styles[status]}`} aria-label={`Status: ${LABELS[status]}`}>
      {LABELS[status]}
    </span>
  )
}
