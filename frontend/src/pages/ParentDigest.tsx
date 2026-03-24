import { useEffect, useState } from 'react'
import { getDigests } from '../api/digests'
import { flagDigest } from '../api/digests'
import type { Digest, User } from '../api/types'
import { SectionCard } from '../components/shared/SectionCard'
import { VocabularyChip } from '../components/shared/VocabularyChip'
import { Toast } from '../components/shared/Toast'
import styles from './ParentDigest.module.css'

const TERM_LABELS: Record<string, string> = {
  autumn: 'Autumn Term',
  spring: 'Spring Term',
  summer: 'Summer Term',
}

interface Props { user: User }  // eslint-disable-line @typescript-eslint/no-unused-vars

export function ParentDigest({ user: _user }: Props) {
  const [digest, setDigest] = useState<Digest | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [flagging, setFlagging] = useState(false)
  const [toast, setToast] = useState<string | null>(null)

  useEffect(() => {
    getDigests()
      .then(list => {
        const sorted = [...list].sort((a, b) => b.week_number - a.week_number)
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

  return (
    <div className={styles.page}>
      {toast && <Toast message={toast} onDismiss={() => setToast(null)} />}
      <div className={styles.content}>

        <header className={styles.weekHeader}>
          <div className={styles.weekMeta}>
            <span>{TERM_LABELS[digest.term] || digest.term}</span>
            <span className={styles.dot}>·</span>
            <span>Week {digest.week_number}</span>
          </div>
          <h1 className={styles.unitTitle}>{digest.unit_title}</h1>
          <p className={styles.reviewedBy}>
            ✓ Reviewed by your child's teacher
          </p>
        </header>

        <div className={styles.sections}>
          <SectionCard title="What your child is learning">
            <p>{digest.plain_english}</p>
          </SectionCard>

          <SectionCard title="What this looks like in school">
            <p>{digest.in_school}</p>
          </SectionCard>

          <SectionCard title="Try this at home" accent>
            <p>{digest.home_activity}</p>
          </SectionCard>

          <SectionCard title="Questions to try at dinner">
            <ol className={styles.questionList}>
              {digest.dinner_table_questions.map((q, i) => (
                <li key={i} className={styles.questionItem}>{q}</li>
              ))}
            </ol>
          </SectionCard>

          {digest.key_vocabulary.length > 0 && (
            <SectionCard title="Words to know">
              <p className={styles.vocabHint}>Tap a word to see what it means.</p>
              <div className={styles.chips}>
                {digest.key_vocabulary.map((entry, i) => (
                  <VocabularyChip key={i} entry={entry} />
                ))}
              </div>
            </SectionCard>
          )}

          {digest.example_questions.length > 0 && (
            <SectionCard title="Example questions">
              <ol className={styles.questionList}>
                {digest.example_questions.map((q, i) => (
                  <li key={i} className={styles.questionItem}>{q}</li>
                ))}
              </ol>
            </SectionCard>
          )}

          {digest.times_table_tip && (
            <div className={styles.tipBox}>
              <span className={styles.tipLabel}>Times tables tip</span>
              <p className={styles.tipText}>{digest.times_table_tip}</p>
            </div>
          )}

          {digest.teacher_note && (
            <div className={styles.teacherNote}>
              <span className={styles.noteLabel}>Note from your teacher</span>
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
