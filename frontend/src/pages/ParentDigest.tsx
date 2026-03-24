import { useEffect, useMemo, useState } from 'react'
import { getDigests, flagDigest } from '../api/digests'
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

const TERM_ORDER: Record<string, number> = { autumn: 0, spring: 1, summer: 2 }

const TERM_COLOURS: Record<string, string> = {
  autumn: '#C97B2E',
  spring: '#2A6049',
  summer: '#2D6A9F',
}

function formatYearGroup(yg: string): string {
  return yg
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase())
}

const WEEKS_PER_TERM = 12

interface Props { user: User }

export function ParentDigest({ user: _user }: Props) {
  const [allDigests, setAllDigests] = useState<Digest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [flagging, setFlagging] = useState(false)
  const [toast, setToast] = useState<string | null>(null)

  // Navigation state
  const [selectedYearGroup, setSelectedYearGroup] = useState<string | null>(null)
  const [selectedTerm, setSelectedTerm] = useState<string | null>(null)
  const [selectedWeek, setSelectedWeek] = useState<number | null>(null)

  useEffect(() => {
    getDigests()
      .then(list => {
        setAllDigests(list)
        // Auto-select latest digest
        if (list.length > 0) {
          const latest = [...list].sort((a, b) => {
            const termDiff = (TERM_ORDER[b.term] ?? 0) - (TERM_ORDER[a.term] ?? 0)
            if (termDiff !== 0) return termDiff
            return b.week_number - a.week_number
          })[0]
          setSelectedYearGroup(latest.year_group)
          setSelectedTerm(latest.term)
          setSelectedWeek(latest.week_number)
        }
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  // Derived filter options
  const yearGroups = useMemo(() => {
    const set = new Set(allDigests.map(d => d.year_group))
    return [...set].sort()
  }, [allDigests])

  const termsForYear = useMemo(() => {
    if (!selectedYearGroup) return []
    const set = new Set(
      allDigests.filter(d => d.year_group === selectedYearGroup).map(d => d.term)
    )
    return [...set].sort((a, b) => (TERM_ORDER[a] ?? 0) - (TERM_ORDER[b] ?? 0))
  }, [allDigests, selectedYearGroup])

  const weeksForTermAndYear = useMemo(() => {
    if (!selectedYearGroup || !selectedTerm) return []
    return allDigests
      .filter(d => d.year_group === selectedYearGroup && d.term === selectedTerm)
      .map(d => d.week_number)
      .sort((a, b) => a - b)
  }, [allDigests, selectedYearGroup, selectedTerm])

  // Current digest based on selections
  const digest = useMemo(() => {
    if (!selectedYearGroup || !selectedTerm || !selectedWeek) return null
    return allDigests.find(
      d => d.year_group === selectedYearGroup
        && d.term === selectedTerm
        && d.week_number === selectedWeek
    ) ?? null
  }, [allDigests, selectedYearGroup, selectedTerm, selectedWeek])

  // Latest digest for "Current Week" shortcut
  const latestDigest = useMemo(() => {
    if (allDigests.length === 0) return null
    return [...allDigests].sort((a, b) => {
      const termDiff = (TERM_ORDER[b.term] ?? 0) - (TERM_ORDER[a.term] ?? 0)
      if (termDiff !== 0) return termDiff
      return b.week_number - a.week_number
    })[0]
  }, [allDigests])

  const isCurrentWeek = latestDigest
    && selectedYearGroup === latestDigest.year_group
    && selectedTerm === latestDigest.term
    && selectedWeek === latestDigest.week_number

  const goToCurrentWeek = () => {
    if (!latestDigest) return
    setSelectedYearGroup(latestDigest.year_group)
    setSelectedTerm(latestDigest.term)
    setSelectedWeek(latestDigest.week_number)
  }

  const handleYearGroupChange = (yg: string) => {
    setSelectedYearGroup(yg)
    // Pick first available term for this year group
    const terms = allDigests
      .filter(d => d.year_group === yg)
      .map(d => d.term)
    const sorted = [...new Set(terms)].sort((a, b) => (TERM_ORDER[a] ?? 0) - (TERM_ORDER[b] ?? 0))
    const firstTerm = sorted[0] ?? null
    setSelectedTerm(firstTerm)
    // Pick first available week for that term
    if (firstTerm) {
      const weeks = allDigests
        .filter(d => d.year_group === yg && d.term === firstTerm)
        .map(d => d.week_number)
        .sort((a, b) => a - b)
      setSelectedWeek(weeks[0] ?? null)
    } else {
      setSelectedWeek(null)
    }
  }

  const handleTermChange = (term: string) => {
    setSelectedTerm(term)
    const weeks = allDigests
      .filter(d => d.year_group === selectedYearGroup && d.term === term)
      .map(d => d.week_number)
      .sort((a, b) => a - b)
    setSelectedWeek(weeks[0] ?? null)
  }

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
  if (allDigests.length === 0) return (
    <div className={styles.empty}>
      <h1>No updates yet</h1>
      <p>Your teacher hasn't published a weekly update yet. Check back soon.</p>
    </div>
  )

  const termColour = digest ? (TERM_COLOURS[digest.term] || TERM_COLOURS.autumn) : TERM_COLOURS.autumn

  return (
    <div className={styles.page}>
      {toast && <Toast message={toast} onDismiss={() => setToast(null)} />}
      <div className={styles.content}>

        {/* ── Navigation bar ── */}
        <nav className={styles.nav} aria-label="Digest navigation">
          <div className={styles.navSelectors}>
            <div className={styles.selectorGroup}>
              <label htmlFor="nav-year" className={styles.selectorLabel}>Year</label>
              <select
                id="nav-year"
                className={styles.selector}
                value={selectedYearGroup ?? ''}
                onChange={e => handleYearGroupChange(e.target.value)}
              >
                {yearGroups.map(yg => (
                  <option key={yg} value={yg}>{formatYearGroup(yg)}</option>
                ))}
              </select>
            </div>

            <div className={styles.selectorGroup}>
              <label htmlFor="nav-term" className={styles.selectorLabel}>Term</label>
              <select
                id="nav-term"
                className={styles.selector}
                value={selectedTerm ?? ''}
                onChange={e => handleTermChange(e.target.value)}
              >
                {termsForYear.map(t => (
                  <option key={t} value={t}>{TERM_LABELS[t] || t}</option>
                ))}
              </select>
            </div>

            <div className={styles.selectorGroup}>
              <label htmlFor="nav-week" className={styles.selectorLabel}>Week</label>
              <select
                id="nav-week"
                className={styles.selector}
                value={selectedWeek ?? ''}
                onChange={e => setSelectedWeek(Number(e.target.value))}
              >
                {weeksForTermAndYear.map(w => (
                  <option key={w} value={w}>Week {w}</option>
                ))}
              </select>
            </div>
          </div>

          {!isCurrentWeek && (
            <button
              className={styles.currentWeekBtn}
              onClick={goToCurrentWeek}
              type="button"
            >
              ↩ Current Week
            </button>
          )}
        </nav>

        {/* ── Digest content ── */}
        {!digest ? (
          <div className={styles.emptyWeek}>
            <p>No digest available for this week yet.</p>
          </div>
        ) : (
          <>
            <header className={styles.weekHeader}>
              <h1 className={styles.unitTitle}>{digest.unit_title}</h1>
              <div className={styles.headerMeta}>
                <p className={styles.reviewedBy}>
                  ✓ Reviewed by your child's teacher
                </p>
              </div>
            </header>

            {/* Term progress */}
            <div className={styles.progressBar}>
              <span className={styles.progressLabel}>Term progress</span>
              <div className={styles.progressTrack}>
                <div
                  className={styles.progressFill}
                  style={{
                    width: `${Math.min(100, (digest.week_number / WEEKS_PER_TERM) * 100)}%`,
                    backgroundColor: termColour,
                  }}
                />
              </div>
              <span className={styles.progressText}>
                Week {digest.week_number} of {WEEKS_PER_TERM}
              </span>
            </div>

            {/* Concept illustration */}
            <div className={styles.illustrationPanel}>
              <ConceptIllustration unitTitle={digest.unit_title} />
            </div>

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
          </>
        )}
      </div>
    </div>
  )
}
