import { useState } from 'react'
import type { VocabEntry } from '../../api/types'
import styles from './VocabularyChip.module.css'

export function VocabularyChip({ entry }: { entry: VocabEntry }) {
  const [open, setOpen] = useState(false)

  return (
    <span className={styles.wrapper}>
      <button
        className={styles.chip}
        onClick={() => setOpen(o => !o)}
        aria-expanded={open}
        aria-label={`${entry.term}: tap to see definition`}
        type="button"
      >
        <span>{entry.term}</span>
        <svg
          className={`${styles.chevronIcon} ${open ? styles.chevronOpen : ''}`}
          width="18" height="18" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          aria-hidden="true"
        >
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </button>
      {open && (
        <span className={styles.definition} role="note">
          {entry.definition}
        </span>
      )}
    </span>
  )
}
