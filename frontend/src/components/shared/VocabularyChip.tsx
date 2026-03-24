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
        <svg className={styles.speakerIcon} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
          <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
          <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
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
