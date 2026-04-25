import { useEffect, useMemo, useState } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import * as Collapsible from '@radix-ui/react-collapsible'
import { getDigests, flagDigest } from '../api/digests'
import type { Digest, User } from '../api/types'
import { SectionCard } from '../components/shared/SectionCard'
import { VocabularyChip } from '../components/shared/VocabularyChip'
import { Toast } from '../components/shared/Toast'
import { ConceptIllustration } from '../components/shared/ConceptIllustration'
import styles from './ParentDigest.module.css'

const WELCOME_KEY = 'bm_seen_welcome_v1'

const SECTION_IDS = ['overview', 'home', 'classroom', 'talk', 'practise'] as const
type SectionId = typeof SECTION_IDS[number]
const SECTION_LABELS: Record<SectionId, string> = {
  overview: 'This week',
  home: 'Home',
  classroom: 'Classroom',
  talk: 'Talk',
  practise: 'Practise',
}

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

// UK academic term definitions relative to an academic start year
// (academic year that starts in September)
function getTermDates(academicStartYear: number) {
  return [
    { name: 'autumn', start: new Date(academicStartYear, 8, 1),      end: new Date(academicStartYear, 11, 20),    totalWeeks: 13 },
    { name: 'spring', start: new Date(academicStartYear + 1, 0, 5),  end: new Date(academicStartYear + 1, 3, 3),  totalWeeks: 13 },
    { name: 'summer', start: new Date(academicStartYear + 1, 3, 20), end: new Date(academicStartYear + 1, 6, 18), totalWeeks: 13 },
  ]
}

// Work out which academic term today falls in and how many weeks in we are
function getCurrentAcademicInfo(today: Date): { term: string; weekInTerm: number; totalWeeks: number } | null {
  const m = today.getMonth() + 1 // 1-based
  const y = today.getFullYear()
  const academicStartYear = m >= 9 ? y : y - 1
  const MS_PER_WEEK = 7 * 24 * 60 * 60 * 1000
  for (const t of getTermDates(academicStartYear)) {
    if (today >= t.start && today <= t.end) {
      const weekInTerm = Math.max(1, Math.floor((today.getTime() - t.start.getTime()) / MS_PER_WEEK) + 1)
      return { term: t.name, weekInTerm, totalWeeks: t.totalWeeks }
    }
  }
  return null // school holiday
}

// Map a calendar-week position to the nearest available digest week index
function mapToAvailableWeek(weekInTerm: number, totalTermWeeks: number, sortedWeeks: number[]): number {
  if (sortedWeeks.length === 0) return 1
  if (sortedWeeks.length === 1) return sortedWeeks[0]
  const progress = Math.min((weekInTerm - 1) / Math.max(1, totalTermWeeks - 1), 1)
  const idx = Math.min(Math.round(progress * (sortedWeeks.length - 1)), sortedWeeks.length - 1)
  return sortedWeeks[idx]
}

// Date to display for a given week number within a term (uses current academic year's dates)
function getWeekDate(term: string, weekNumber: number): string {
  const today = new Date()
  const m = today.getMonth() + 1
  const academicStartYear = m >= 9 ? today.getFullYear() : today.getFullYear() - 1
  const termDef = getTermDates(academicStartYear).find(t => t.name === term)
  if (!termDef) return ''
  const d = new Date(termDef.start)
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

interface Props { user: User | null }

export function ParentDigest({ user: _user }: Props) {
  const [allDigests, setAllDigests] = useState<Digest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [flagging, setFlagging] = useState(false)
  const [toast, setToast] = useState<string | null>(null)

  const [selectedYearGroup, setSelectedYearGroup] = useState<string | null>(null)
  const [selectedTerm, setSelectedTerm] = useState<string | null>(null)
  const [selectedWeek, setSelectedWeek] = useState<number | null>(null)

  const [navOpen, setNavOpen] = useState(false)
  const [flagOpen, setFlagOpen] = useState(false)
  const [flagNote, setFlagNote] = useState('')
  const [showWelcome, setShowWelcome] = useState(() => {
    if (typeof window === 'undefined') return false
    return window.localStorage.getItem(WELCOME_KEY) !== '1'
  })

  const dismissWelcome = () => {
    setShowWelcome(false)
    try { window.localStorage.setItem(WELCOME_KEY, '1') } catch {}
  }

  const [activeSection, setActiveSection] = useState<SectionId>('overview')

  const scrollToSection = (id: SectionId) => {
    const el = document.getElementById(`section-${id}`)
    if (!el) return
    const headerOffset = 56 + 56 + 8 // AppShell + sticky chip strip + small gap
    const top = el.getBoundingClientRect().top + window.pageYOffset - headerOffset
    window.scrollTo({ top, behavior: 'smooth' })
  }

  useEffect(() => {
    getDigests()
      .then(list => {
        setAllDigests(list)
        if (list.length === 0) return

        // Try to land on the term/week that matches today's calendar position
        const termInfo = getCurrentAcademicInfo(new Date())
        if (termInfo) {
          const yearGroups = [...new Set(list.map(d => d.year_group))].sort()
          const firstYg = yearGroups[0]
          const availWeeks = list
            .filter(d => d.year_group === firstYg && d.term === termInfo.term)
            .map(d => d.week_number)
            .sort((a, b) => a - b)
          if (availWeeks.length > 0) {
            const week = mapToAvailableWeek(termInfo.weekInTerm, termInfo.totalWeeks, availWeeks)
            setSelectedYearGroup(firstYg)
            setSelectedTerm(termInfo.term)
            setSelectedWeek(week)
            return
          }
        }

        // Fallback: most recent digest by term order
        const latest = [...list].sort((a, b) => {
          const td = (TERM_ORDER[b.term] ?? 0) - (TERM_ORDER[a.term] ?? 0)
          return td !== 0 ? td : b.week_number - a.week_number
        })[0]
        setSelectedYearGroup(latest.year_group)
        setSelectedTerm(latest.term)
        setSelectedWeek(latest.week_number)
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

  // Scroll-spy: highlight the chip for whichever section is currently in view
  useEffect(() => {
    if (!digest) return
    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const id = entry.target.id.replace('section-', '') as SectionId
            if (SECTION_IDS.includes(id)) setActiveSection(id)
          }
        })
      },
      { rootMargin: '-30% 0px -55% 0px', threshold: 0 }
    )
    SECTION_IDS.forEach(id => {
      const el = document.getElementById(`section-${id}`)
      if (el) observer.observe(el)
    })
    return () => observer.disconnect()
  }, [digest])

  // The "current" week is determined from today's calendar date
  const currentCalendarTarget = useMemo(() => {
    const termInfo = getCurrentAcademicInfo(new Date())
    if (!termInfo || !selectedYearGroup) return null
    const available = allDigests
      .filter(d => d.year_group === selectedYearGroup && d.term === termInfo.term)
      .map(d => d.week_number)
      .sort((a, b) => a - b)
    if (available.length === 0) return null
    return { term: termInfo.term, week: mapToAvailableWeek(termInfo.weekInTerm, termInfo.totalWeeks, available) }
  }, [allDigests, selectedYearGroup])

  const isCurrentWeek = currentCalendarTarget
    && selectedTerm === currentCalendarTarget.term
    && selectedWeek === currentCalendarTarget.week

  const goToCurrentWeek = () => {
    if (currentCalendarTarget) {
      setSelectedTerm(currentCalendarTarget.term)
      setSelectedWeek(currentCalendarTarget.week)
    }
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
      await flagDigest(digest.id, flagNote.trim() || 'Flagged by parent')
      setToast('Thanks — your teacher has been notified.')
      setFlagOpen(false)
      setFlagNote('')
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
  const weekDate = digest ? getWeekDate(digest.term, digest.week_number) : ''
  const totalWeeksInTerm = weeksForTermAndYear.length > 0 ? Math.max(...weeksForTermAndYear) : 12
  const ttNum = digest?.times_table_tip ? parseTimesTableNumber(digest.times_table_tip) : null
  const ttMultiples = ttNum ? Array.from({ length: 10 }, (_, i) => ttNum * (i + 1)) : []

  return (
    <div className={styles.page}>
      {toast && <Toast message={toast} onDismiss={() => setToast(null)} />}
      <div className={styles.content}>

        {/* ── First-time welcome card ── */}
        {showWelcome && (
          <aside className={styles.welcomeCard} aria-label="Welcome">
            <div className={styles.welcomeHeader}>
              <h2 className={styles.welcomeTitle}>Welcome to your weekly maths update</h2>
              <button onClick={dismissWelcome} className={styles.welcomeDismiss} type="button" aria-label="Dismiss welcome">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <p className={styles.welcomeBody}>
              Each week your teacher publishes a short digest of what your child is learning in maths. A few things to look out for:
            </p>
            <ul className={styles.welcomeList}>
              <li><span className={styles.welcomeListIcon} aria-hidden="true"><HomeIcon /></span><span><strong>Try this at home</strong> — a five-minute activity for your evening.</span></li>
              <li><span className={styles.welcomeListIcon} aria-hidden="true"><CutleryIcon /></span><span><strong>Dinner-table questions</strong> — natural ways to bring maths into chat.</span></li>
              <li><span className={styles.welcomeListIcon} aria-hidden="true"><ChatIcon /></span><span><strong>A note from your teacher</strong> — anything specific to this week.</span></li>
            </ul>
            <div className={styles.welcomeActions}>
              <button onClick={dismissWelcome} className={styles.welcomePrimaryBtn} type="button">
                Got it
              </button>
            </div>
          </aside>
        )}

        {/* ── Navigation (collapsed by default; expand to browse other weeks) ── */}
        <Collapsible.Root open={navOpen} onOpenChange={setNavOpen} asChild>
          <nav className={styles.nav} aria-label="Digest navigation">
            <div className={styles.navRow}>
              <Collapsible.Trigger asChild>
                <button className={styles.navTrigger} type="button">
                  <span>{navOpen ? 'Hide' : 'Browse other weeks'}</span>
                  <svg
                    className={`${styles.navTriggerIcon} ${navOpen ? styles.navTriggerIconOpen : ''}`}
                    width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <polyline points="6 9 12 15 18 9"/>
                  </svg>
                </button>
              </Collapsible.Trigger>

              {!isCurrentWeek && (
                <button className={styles.currentWeekBtn} onClick={goToCurrentWeek} type="button">
                  Jump to current week
                </button>
              )}
            </div>

            <Collapsible.Content className={styles.navContent}>
              <div className={styles.navPills}>
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
            </Collapsible.Content>
          </nav>
        </Collapsible.Root>

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
                <div className={styles.progressFill} style={{ width: `${Math.min(100, (digest.week_number / totalWeeksInTerm) * 100)}%`, backgroundColor: termColour }} />
              </div>
              <span className={styles.progressText}>Week {digest.week_number} of {totalWeeksInTerm}</span>
            </div>

            {/* Sticky chip strip — section navigation */}
            <div className={styles.chipStrip} role="navigation" aria-label="Sections">
              <div className={styles.chipStripInner}>
                {SECTION_IDS.map(id => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => scrollToSection(id)}
                    className={`${styles.sectionChip} ${activeSection === id ? styles.sectionChipActive : ''}`}
                    aria-current={activeSection === id ? 'true' : undefined}
                  >
                    {SECTION_LABELS[id]}
                  </button>
                ))}
              </div>
            </div>

            <div className={styles.sections}>

              {/* 1. What's happening this week — overview + teacher note */}
              <div id="section-overview">
                <SectionCard subtitle="What's happening this week" icon={<BookIcon />}>
                  {digest.teacher_note && (
                    <div className={styles.teacherNoteBlock}>
                      <span className={styles.teacherNoteLabel}>From your teacher</span>
                      <p>{digest.teacher_note}</p>
                    </div>
                  )}
                  <p>{digest.plain_english}</p>
                </SectionCard>
              </div>

              {/* 2. Try this at home — the action */}
              <div id="section-home">
                <SectionCard subtitle="Try this at home" icon={<HomeIcon />} accent>
                  <div className={styles.activityCard}>
                    <span className={styles.activityTitle}>Five-minute activity</span>
                    <p className={styles.activityBody}>{digest.home_activity}</p>
                  </div>
                </SectionCard>
              </div>

              {/* 3. In the classroom — context + illustration */}
              <div id="section-classroom">
                <SectionCard subtitle="In the classroom" icon={<SchoolIcon />}>
                  <p>{digest.in_school}</p>
                  <div className={styles.illustrationWrap}>
                    <ConceptIllustration unitTitle={digest.unit_title} />
                  </div>
                </SectionCard>
              </div>

              {/* 4. Talk about it — dinner table + vocabulary */}
              {(digest.dinner_table_questions.length > 0 || digest.key_vocabulary.length > 0) && (
                <div id="section-talk">
                  <SectionCard subtitle="Talk about it" icon={<CutleryIcon />}>
                    {digest.dinner_table_questions.length > 0 && (
                      <div className={styles.sectionGroup}>
                        <h3 className={styles.sectionGroupHeading}>Dinner-table questions</h3>
                        <p className={styles.hint}><em>Try slipping these into natural conversation rather than testing directly.</em></p>
                        <ol className={styles.questionList}>
                          {digest.dinner_table_questions.map((q, i) => (
                            <li key={i} className={styles.questionItem}>
                              <span className={styles.questionNum}>{i + 1}</span>
                              <span>{q}</span>
                            </li>
                          ))}
                        </ol>
                      </div>
                    )}
                    {digest.key_vocabulary.length > 0 && (
                      <div className={styles.sectionGroup}>
                        <h3 className={styles.sectionGroupHeading}>Key vocabulary</h3>
                        <p className={styles.hint}>Tap a word to see what it means.</p>
                        <div className={styles.vocabList}>
                          {digest.key_vocabulary.map((entry, i) => (
                            <VocabularyChip key={i} entry={entry} />
                          ))}
                        </div>
                      </div>
                    )}
                  </SectionCard>
                </div>
              )}

              {/* 5. Practise & stretch — example questions + times table tip */}
              {(digest.example_questions.length > 0 || digest.times_table_tip) && (
                <div id="section-practise">
                  <SectionCard subtitle="Practise & stretch" icon={<NumbersIcon />}>
                    {digest.example_questions.length > 0 && (
                      <div className={styles.sectionGroup}>
                        <h3 className={styles.sectionGroupHeading}>Example questions</h3>
                        <p className={styles.hint}>Try these with your child.</p>
                        <ol className={styles.questionList}>
                          {digest.example_questions.map((q, i) => (
                            <li key={i} className={styles.questionItem}>
                              <span className={styles.questionNum}>{i + 1}</span>
                              <span className={styles.questionText}>{q}</span>
                            </li>
                          ))}
                        </ol>
                      </div>
                    )}
                    {digest.times_table_tip && (
                      <div className={styles.sectionGroup}>
                        <h3 className={styles.sectionGroupHeading}>Times-table tip</h3>
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
                      </div>
                    )}
                  </SectionCard>
                </div>
              )}
            </div>

            {/* Footer — meta + feedback in one closing block */}
            <footer className={styles.footer}>
              <div className={styles.footerFlag}>
                <span className={styles.footerFlagLabel}>Something not right?</span>

                <Dialog.Root open={flagOpen} onOpenChange={setFlagOpen}>
                  <Dialog.Trigger asChild>
                    <button className={styles.footerFlagBtn} type="button">Let your teacher know</button>
                  </Dialog.Trigger>
                  <Dialog.Portal>
                    <Dialog.Overlay className={styles.dialogOverlay} />
                    <Dialog.Content className={styles.dialogContent} aria-describedby="flag-description">
                      <Dialog.Title className={styles.dialogTitle}>
                        Tell your teacher about this week's update?
                      </Dialog.Title>
                      <Dialog.Description id="flag-description" className={styles.dialogDescription}>
                        Your teacher will get a note saying you flagged this week's digest. Add a quick reason below if it would help.
                      </Dialog.Description>
                      <textarea
                        className={styles.dialogTextarea}
                        value={flagNote}
                        onChange={e => setFlagNote(e.target.value)}
                        placeholder="e.g. The home activity was too tricky for my child this week (optional)"
                        rows={3}
                        aria-label="Optional note for the teacher"
                      />
                      <div className={styles.dialogActions}>
                        <Dialog.Close asChild>
                          <button className={styles.dialogSecondary} type="button">Cancel</button>
                        </Dialog.Close>
                        <button
                          className={styles.dialogPrimary}
                          onClick={handleFlag}
                          disabled={flagging}
                          type="button"
                        >
                          {flagging ? 'Sending…' : 'Send to teacher'}
                        </button>
                      </div>
                    </Dialog.Content>
                  </Dialog.Portal>
                </Dialog.Root>
              </div>
              <div className={styles.footerMeta}>
                <p>Beaumont Primary School · Maths Parent Companion</p>
                <p>Based on White Rose Maths · {selectedTerm ? TERM_LABELS[selectedTerm] : ''} 2026</p>
              </div>
            </footer>
          </>
        )}
      </div>
    </div>
  )
}
