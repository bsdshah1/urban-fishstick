import { useEffect, useState } from 'react'
import { getDigests } from '../api/digests'
import { flagDigest } from '../api/digests'
import type { Digest, User } from '../api/types'
import { SectionCard } from '../components/shared/SectionCard'
import { VocabularyChip } from '../components/shared/VocabularyChip'
import { Toast } from '../components/shared/Toast'
import { ConceptIllustration } from '../components/shared/ConceptIllustration'
import styles from './ParentDigest.module.css'

const TERM_LABELS: Record<string, string> = {
  autumn: 'Autumn Term',
  spring: 'Spring Term',
  summer: 'Summer Term',
}

const TERM_COLOURS: Record<string, string> = {
  autumn: '#C97B2E',
  spring: '#2A6049',
  summer: '#2D6A9F',
}

interface Props { user: User }  // eslint-disable-line @typescript-eslint/no-unused-vars

export function ParentDigest({ user: _user }: Props) {
  const [digest, setDigest] = useState<Digest | null>(null)
  const [allDigests, setAllDigests] = useState<Digest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [flagging, setFlagging] = useState(false)
  const [toast, setToast] = useState<string | null>(null)

  useEffect(() => {
    getDigests()
      .then(list => {
        const sorted = [...list].sort((a, b) => b.week_number - a.week_number)
        setAllDigests(sorted)
        setDigest(sorted[0] || null)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const handleFlag = async () => {
    if (!digest) return
    setFlagging(true)
    try {
      await flagDigest(digest.id, 'Flagged by parent')
      setToast('Thank you — your teacher has been notified.')
    } catch {
      setToast('Could not send feedback. Please try again.')
    } finally {
      setFlagging(false)
    }
  }

  if (loading) return <div className={styles.loading}>Loading this week's update…</div>
  if (error) return <div className={styles.error}>{error}</div>
  if (!digest) return (
    <div className={styles.empty}>
      <h1>No updates yet</h1>
      <p>Your teacher hasn't published a weekly update yet. Check back soon.</p>
    </div>
  )

  const termColour = TERM_COLOURS[digest.term] || TERM_COLOURS.autumn

  return (
    <div className={styles.page}>
      {toast && <Toast message={toast} onDismiss={() => setToast(null)} />}
      <div className={styles.content}>

        <header className={styles.weekHeader}>
          <div className={styles.weekMeta}>
            <span className={styles.termBadge} style={{ background: termColour }}>
              {TERM_LABELS[digest.term] || digest.term}
            </span>
            <span className={styles.weekPill}>Week {digest.week_number}</span>
          </div>
          <h1 className={styles.unitTitle}>{digest.unit_title}</h1>
          <p className={styles.reviewedBy}>
            ✓ Reviewed by your child's teacher
          </p>
        </header>

        {/* Visual concept illustration */}
        <div className={styles.illustrationPanel}>
          <ConceptIllustration unitTitle={digest.unit_title} />
        </div>

        {/* Previous weeks strip */}
        {allDigests.length > 1 && (
          <div className={styles.weekStrip}>
            <span className={styles.weekStripLabel}>Recent weeks</span>
            <div className={styles.weekDots}>
              {allDigests.slice(0, 6).map((d, i) => (
                <button
                  key={d.id}
                  className={`${styles.weekDot} ${d.id === digest.id ? styles.weekDotActive : ''}`}
                  onClick={() => setDigest(d)}
                  title={`Week ${d.week_number}: ${d.unit_title}`}
                  type="button"
                  style={d.id === digest.id ? { background: termColour, borderColor: termColour } : undefined}
                >
                  {i === 0 && d.id !== digest.id
                    ? <span className={styles.newDot} />
                    : null}
                  {d.week_number}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className={styles.sections}>
          <SectionCard title="What your child is learning" icon="📖">
            <p>{digest.plain_english}</p>
          </SectionCard>

          <SectionCard title="What this looks like in school" icon="🏫">
            <p>{digest.in_school}</p>
          </SectionCard>

          <SectionCard title="Try this at home" icon="🏠" accent>
            <p>{digest.home_activity}</p>
          </SectionCard>

          <SectionCard title="Questions to try at dinner" icon="🍽️">
            <ol className={styles.questionList}>
              {digest.dinner_table_questions.map((q, i) => (
                <li key={i} className={styles.questionItem}>
                  <span className={styles.questionNum}>{i + 1}</span>
                  <span>{q}</span>
                </li>
              ))}
            </ol>
          </SectionCard>

          {digest.key_vocabulary.length > 0 && (
            <SectionCard title="Words to know" icon="💬">
              <p className={styles.vocabHint}>Tap a word to see what it means.</p>
              <div className={styles.chips}>
                {digest.key_vocabulary.map((entry, i) => (
                  <VocabularyChip key={i} entry={entry} />
                ))}
              </div>
            </SectionCard>
          )}

          {digest.example_questions.length > 0 && (
            <SectionCard title="Example questions" icon="✏️">
              <ol className={styles.questionList}>
                {digest.example_questions.map((q, i) => (
                  <li key={i} className={styles.questionItem}>
                    <span className={styles.questionNum}>{i + 1}</span>
                    <span>{q}</span>
                  </li>
                ))}
              </ol>
            </SectionCard>
          )}

          {digest.times_table_tip && (
            <div className={styles.tipBox}>
              <span className={styles.tipLabel}>⭐ Times tables tip</span>
              <p className={styles.tipText}>{digest.times_table_tip}</p>
            </div>
          )}

          {digest.teacher_note && (
            <div className={styles.teacherNote}>
              <span className={styles.noteLabel}>✉️ Note from your teacher</span>
              <p>{digest.teacher_note}</p>
            </div>
          )}
        </div>

        <div className={styles.flagArea}>
          <p className={styles.flagText}>Something not right?</p>
          <button
            className={styles.flagBtn}
            onClick={handleFlag}
            disabled={flagging}
            type="button"
          >
            {flagging ? 'Sending…' : 'Let us know'}
          </button>
        </div>

      </div>
    </div>
  )
}
