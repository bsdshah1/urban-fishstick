import { useEffect, useMemo, useState } from 'react'
import { getDigests, flagDigest } from '../api/digests'
import type { Digest, User } from '../api/types'
import { SectionCard } from '../components/shared/SectionCard'
import { VocabularyChip } from '../components/shared/VocabularyChip'
import { Toast } from '../components/shared/Toast'
import { ConceptIllustration } from '../components/shared/ConceptIllustration'
import styles from './ParentDigest.module.css'

// ── SVG Icons ──────────────────────────────────────────────────────────────

function BookIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
      <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
    </svg>
  )
}

function SchoolIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
      <polyline points="9 22 9 12 15 12 15 22"/>
    </svg>
  )
}

function HomeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
      <polyline points="9 22 9 12 15 12 15 22"/>
      <path d="M12 2v4"/>
    </svg>
  )
}

function CutleryIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="2" x2="12" y2="22"/>
      <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
    </svg>
  )
}

function KeyIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
      <line x1="3" y1="9" x2="21" y2="9"/>
      <line x1="3" y1="15" x2="21" y2="15"/>
      <line x1="9" y1="9" x2="9" y2="21"/>
    </svg>
  )
}

function NumbersIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="8" height="8" rx="1"/>
      <rect x="13" y="3" width="8" height="8" rx="1"/>
      <rect x="3" y="13" width="8" height="8" rx="1"/>
      <rect x="13" y="13" width="8" height="8" rx="1"/>
    </svg>
  )
}

function LightbulbIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="9" y1="18" x2="15" y2="18"/>
      <line x1="10" y1="22" x2="14" y2="22"/>
      <path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/>
    </svg>
  )
}

function ChatIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    </svg>
  )
}

// ── Helpers ────────────────────────────────────────────────────────────────

const TERM_LABELS: Record<string, string> = {
  autumn: 'Autumn Term',
  spring: 'Spring Term',
  summer: 'Summer Term',
}

const TERM_ORDER: Record<string, number> = { autumn: 0, spring: 1, summer: 2 }

// Approximate term start dates (Monday of first week) for 2026/2027
const TERM_STARTS: Record<string, Record<string, Date>> = {
  autumn: { eyfs: new Date('2026-09-07'), year_1: new Date('2026-09-07'), year_2: new Date('2026-09-07'), year_3: new Date('2026-09-07'), year_4: new Date('2026-09-07'), year_5: new Date('2026-09-07'), year_6: new Date('2026-09-07') },
  spring: { eyfs: new Date('2027-01-04'), year_1: new Date('2027-01-04'), year_2: new Date('2027-01-04'), year_3: new Date('2027-01-04'), year_4: new Date('2027-01-04'), year_5: new Date('2027-01-04'), year_6: new Date('2027-01-04') },
  summer: { eyfs: new Date('2027-04-19'), year_1: new Date('2027-04-19'), year_2: new Date('2027-04-19'), year_3: new Date('2027-04-19'), year_4: new Date('2027-04-19'), year_5: new Date('2027-04-19'), year_6: new Date('2027-04-19') },
}

function getWeekDate(term: string, _yearGroup: string, weekNumber: number): string {
  const starts = TERM_STARTS[term]
  const base = starts ? (starts[_yearGroup] ?? starts['year_1']) : null
  if (!base) return ''
  const d = new Date(base)
  d.setDate(d.getDate() + (weekNumber - 1) * 7)
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
}

function formatYearGroup(yg: string): string {
  if (yg === 'eyfs') return 'EYFS'
  return yg.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function parseTimesTableNumber(tip: string): number | null {
  const match = tip.match(/(\d+)\s*(?:times table|×\s*table)/i)
  return match ? parseInt(match[1], 10) : null
}

const DIFFICULTY_LABELS = ['EXPECTED', 'EXPECTED', 'EXPECTED', 'INTERMEDIATE', 'INTERMEDIATE', 'INTERMEDIATE', 'EXCEEDING', 'EXCEEDING', 'EXCEEDING']
const DIFFICULTY_STYLES: Record<string, string> = {
  EXPECTED: styles.badgeExpected,
  INTERMEDIATE: styles.badgeIntermediate,
  EXCEEDING: styles.badgeExceeding,
}

const WEEKS_PER_TERM = 12

interface Props { user: User }

export function ParentDigest({ user: _user }: Props) {
  const [allDigests, setAllDigests] = useState<Digest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [flagging, setFlagging] = useState(false)
  const [toast, setToast] = useState<string | null>(null)

  const [selectedYearGroup, setSelectedYearGroup] = useState<string | null>(null)
  const [selectedTerm, setSelectedTerm] = useState<string | null>(null)
  const [selectedWeek, setSelectedWeek] = useState<number | null>(null)

  useEffect(() => {
    getDigests()
      .then(list => {
        setAllDigests(list)
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

  const digest = useMemo(() => {
    if (!selectedYearGroup || !selectedTerm || !selectedWeek) return null
    return allDigests.find(
      d => d.year_group === selectedYearGroup
        && d.term === selectedTerm
        && d.week_number === selectedWeek
    ) ?? null
  }, [allDigests, selectedYearGroup, selectedTerm, selectedWeek])

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
    const terms = allDigests.filter(d => d.year_group === yg).map(d => d.term)
    const sorted = [...new Set(terms)].sort((a, b) => (TERM_ORDER[a] ?? 0) - (TERM_ORDER[b] ?? 0))
    const firstTerm = sorted[0] ?? null
    setSelectedTerm(firstTerm)
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

  const termColour = digest ? ({ autumn: '#C97B2E', spring: '#2A6049', summer: '#2D6A9F' }[digest.term] ?? '#2A6049') : '#2A6049'
  const weekDate = digest ? getWeekDate(digest.term, digest.year_group, digest.week_number) : ''
  const ttNum = digest?.times_table_tip ? parseTimesTableNumber(digest.times_table_tip) : null
  const ttMultiples = ttNum ? Array.from({ length: 10 }, (_, i) => ttNum * (i + 1)) : []

  return (
    <div className={styles.page}>
      {toast && <Toast message={toast} onDismiss={() => setToast(null)} />}
      <div className={styles.content}>

        {/* ── Navigation ── */}
        <nav className={styles.nav} aria-label="Digest navigation">
          <div className={styles.navPills}>
            {/* Year pill — dark */}
            <div className={styles.pillWrap}>
              <select
                className={`${styles.pill} ${styles.pillDark}`}
                value={selectedYearGroup ?? ''}
                onChange={e => handleYearGroupChange(e.target.value)}
                aria-label="Year group"
              >
                {yearGroups.map(yg => (
                  <option key={yg} value={yg}>{formatYearGroup(yg)}</option>
                ))}
              </select>
            </div>

            {/* Term pill */}
            <div className={styles.pillWrap}>
              <select
                className={styles.pill}
                value={selectedTerm ?? ''}
                onChange={e => handleTermChange(e.target.value)}
                aria-label="Term"
              >
                {termsForYear.map(t => (
                  <option key={t} value={t}>{TERM_LABELS[t] || t}</option>
                ))}
              </select>
            </div>

            {/* Week pill */}
            <div className={styles.pillWrap}>
              <select
                className={styles.pill}
                value={selectedWeek ?? ''}
                onChange={e => setSelectedWeek(Number(e.target.value))}
                aria-label="Week"
              >
                {weeksForTermAndYear.map(w => (
                  <option key={w} value={w}>Week {w}</option>
                ))}
              </select>
            </div>
          </div>

          {!isCurrentWeek && (
            <button className={styles.currentWeekBtn} onClick={goToCurrentWeek} type="button">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
              Current Week
            </button>
          )}
        </nav>

        {/* ── Digest content ── */}
        {!digest ? (
          <div className={styles.emptyWeek}><p>No digest available for this week yet.</p></div>
        ) : (
          <>
            <header className={styles.weekHeader}>
              <h1 className={styles.unitTitle}>{digest.unit_title}</h1>
              {weekDate && (
                <p className={styles.weekDate}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
                  </svg>
                  Week of {weekDate}
                </p>
              )}
            </header>

            {/* Term progress */}
            <div className={styles.progressBar}>
              <span className={styles.progressLabel}>Term progress</span>
              <div className={styles.progressTrack}>
                <div className={styles.progressFill} style={{ width: `${Math.min(100, (digest.week_number / WEEKS_PER_TERM) * 100)}%`, backgroundColor: termColour }} />
              </div>
              <span className={styles.progressText}>Week {digest.week_number} of {WEEKS_PER_TERM}</span>
            </div>

            <div className={styles.sections}>

              {/* Learning Objective */}
              <SectionCard category="Learning Objective" subtitle="In Plain English" icon={<BookIcon />}>
                <p>{digest.plain_english}</p>
              </SectionCard>

              {/* Classroom Practice */}
              <SectionCard category="Classroom Practice" subtitle="What This Looks Like in School" icon={<SchoolIcon />}>
                <p>{digest.in_school}</p>
                <div className={styles.illustrationWrap}>
                  <ConceptIllustration unitTitle={digest.unit_title} />
                </div>
              </SectionCard>

              {/* Home Support */}
              <SectionCard category="Home Support" subtitle="Home Activity" icon={<HomeIcon />} accent>
                <div className={styles.activityCard}>
                  <div className={styles.activityHeader}>
                    <span className={styles.activityTitle}>Try This at Home</span>
                    <span className={`${styles.diffBadge} ${styles.badgeEasy}`}>Easy</span>
                  </div>
                  <p className={styles.activityBody}>{digest.home_activity}</p>
                </div>
              </SectionCard>

              {/* Conversation Starters */}
              {digest.dinner_table_questions.length > 0 && (
                <SectionCard category="Conversation Starters" subtitle="Dinner Table Questions" icon={<CutleryIcon />}>
                  <p className={styles.hint}><em>Try slipping these into natural conversation rather than testing directly.</em></p>
                  <ol className={styles.questionList}>
                    {digest.dinner_table_questions.map((q, i) => (
                      <li key={i} className={styles.questionItem}>
                        <span className={styles.questionNum}>{i + 1}</span>
                        <span>{q}</span>
                      </li>
                    ))}
                  </ol>
                </SectionCard>
              )}

              {/* Key Terms */}
              {digest.key_vocabulary.length > 0 && (
                <SectionCard category="Key Terms" subtitle="Key Vocabulary" icon={<KeyIcon />}>
                  <p className={styles.hint}>Tap a word to see its definition</p>
                  <div className={styles.vocabList}>
                    {digest.key_vocabulary.map((entry, i) => (
                      <VocabularyChip key={i} entry={entry} />
                    ))}
                  </div>
                </SectionCard>
              )}

              {/* Practice Questions */}
              {digest.example_questions.length > 0 && (
                <SectionCard category="Practice Questions" subtitle="Example Questions" icon={<NumbersIcon />}>
                  <p className={styles.hint}>Try these with your child — questions are organised by difficulty level.</p>
                  <ol className={styles.questionList}>
                    {digest.example_questions.map((q, i) => {
                      const difficulty = DIFFICULTY_LABELS[i] ?? 'EXPECTED'
                      return (
                        <li key={i} className={styles.questionItem}>
                          <span className={styles.questionNum}>{i + 1}</span>
                          <span className={styles.questionText}>{q}</span>
                          <span className={`${styles.diffBadge} ${DIFFICULTY_STYLES[difficulty]}`}>{difficulty}</span>
                        </li>
                      )
                    })}
                  </ol>
                </SectionCard>
              )}

              {/* Weekly Focus — Times Table */}
              {digest.times_table_tip && (
                <SectionCard category="Weekly Focus" subtitle="Times Table Tip of the Week" icon={<LightbulbIcon />}>
                  <div className={styles.tipContent}>
                    <p className={styles.tipText}>{digest.times_table_tip}</p>
                    {ttMultiples.length > 0 && (
                      <div className={styles.multiples}>
                        {ttMultiples.map(n => (
                          <span key={n} className={styles.multipleChip}>{n}</span>
                        ))}
                      </div>
                    )}
                  </div>
                </SectionCard>
              )}

              {/* Teacher Note */}
              {digest.teacher_note && (
                <SectionCard category="A Note from Your Teacher" subtitle="Class Teacher" icon={<ChatIcon />}>
                  <p>{digest.teacher_note}</p>
                </SectionCard>
              )}
            </div>

            {/* Footer */}
            <footer className={styles.footer}>
              <p>Beaumont Primary School · Maths Parent Companion</p>
              <p>Based on White Rose Maths · {selectedTerm ? TERM_LABELS[selectedTerm] : ''} 2026</p>
            </footer>

            <div className={styles.flagArea}>
              <p className={styles.flagText}>Something not right?</p>
              <button className={styles.flagBtn} onClick={handleFlag} disabled={flagging} type="button">
                {flagging ? 'Sending…' : 'Let us know'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
