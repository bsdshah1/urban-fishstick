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
        {entry.term}
      </button>
      {open && (
        <span className={styles.definition} role="tooltip">
          {entry.definition}
        </span>
      )}
    </span>
  )
}
