import { useEffect, useState, useCallback } from 'react'
import { getDigests, approveDigest, publishDigest, updateDigest, generateDigest } from '../api/digests'
import type { Digest, User } from '../api/types'
import { StatusBadge } from '../components/shared/StatusBadge'
import { Button } from '../components/shared/Button'
import { Toast } from '../components/shared/Toast'
import styles from './TeacherDashboard.module.css'

const TERM_LABELS: Record<string, string> = {
  autumn: 'Autumn Term', spring: 'Spring Term', summer: 'Summer Term',
}

function InlineField({
  label, value, multiline, onSave,
}: {
  label: string; value: string; multiline?: boolean; onSave: (v: string) => Promise<void>
}) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value)
  const [saving, setSaving] = useState(false)

  const save = async () => {
    if (draft === value) { setEditing(false); return }
    setSaving(true)
    await onSave(draft)
    setSaving(false)
    setEditing(false)
  }

  if (!editing) {
    return (
      <div className={styles.inlineField}>
        <div className={styles.fieldLabel}>{label}</div>
        <div
          className={styles.fieldValue}
          onClick={() => setEditing(true)}
          role="button"
          tabIndex={0}
          onKeyDown={e => e.key === 'Enter' && setEditing(true)}
          aria-label={`Edit ${label}`}
          title="Click to edit"
        >
          {value || <span className={styles.empty}>Click to add…</span>}
          <span className={styles.editHint}>Edit</span>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.inlineField}>
      <div className={styles.fieldLabel}>{label}</div>
      {multiline ? (
        <textarea
          className={styles.textarea}
          value={draft}
          onChange={e => setDraft(e.target.value)}
          rows={4}
          autoFocus
        />
      ) : (
        <input
          className={styles.input}
          value={draft}
          onChange={e => setDraft(e.target.value)}
          autoFocus
        />
      )}
      <div className={styles.editActions}>
        <Button variant="primary" onClick={save} loading={saving} type="button">Save</Button>
        <Button variant="ghost" onClick={() => { setDraft(value); setEditing(false) }} type="button">Cancel</Button>
      </div>
    </div>
  )
}

interface Props { user: User }

export function TeacherDashboard({ user: _user }: Props) {
  const [digests, setDigests] = useState<Digest[]>([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<number | null>(null)
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null)
  const [generating, setGenerating] = useState(false)
  const [showGenForm, setShowGenForm] = useState(false)
  const [genTitle, setGenTitle] = useState('')

  const reload = useCallback(() => {
    getDigests().then(setDigests).finally(() => setLoading(false))
  }, [])

  useEffect(() => { reload() }, [reload])

  const notify = (msg: string, type: 'success' | 'error' = 'success') =>
    setToast({ msg, type })

  const handleApprove = async (id: number) => {
    try {
      const updated = await approveDigest(id)
      setDigests(ds => ds.map(d => d.id === id ? updated : d))
      notify('Digest approved.')
    } catch (e: unknown) { notify(e instanceof Error ? e.message : 'Failed', 'error') }
  }

  const handlePublish = async (id: number) => {
    try {
      const updated = await publishDigest(id)
      setDigests(ds => ds.map(d => d.id === id ? updated : d))
      notify('Digest published — parents can now see it.')
    } catch (e: unknown) { notify(e instanceof Error ? e.message : 'Failed', 'error') }
  }

  const handleUpdate = async (id: number, field: string, value: string) => {
    try {
      const updated = await updateDigest(id, { [field]: value })
      setDigests(ds => ds.map(d => d.id === id ? updated : d))
    } catch (e: unknown) { notify(e instanceof Error ? e.message : 'Save failed', 'error') }
  }

  const handleGenerate = async () => {
    if (!genTitle.trim()) return
    setGenerating(true)
    try {
      const newDigest = await generateDigest({
        year_group: 'year_2', term: 'autumn',
        week_number: digests.length + 1,
        unit_title: genTitle.trim(),
      })
      setDigests(ds => [newDigest, ...ds])
      setShowGenForm(false)
      setGenTitle('')
      setExpanded(newDigest.id)
      notify('Draft generated — review and approve before publishing.')
    } catch (e: unknown) { notify(e instanceof Error ? e.message : 'Generation failed', 'error') }
    finally { setGenerating(false) }
  }

  if (loading) return <div className={styles.loading}>Loading digests…</div>

  return (
    <div className={styles.page}>
      {toast && <Toast message={toast.msg} type={toast.type} onDismiss={() => setToast(null)} />}
      <div className={styles.container}>

        <div className={styles.topBar}>
          <div>
            <h1 className={styles.pageTitle}>Year 2 — Weekly Review</h1>
            <p className={styles.subtitle}>Review, edit, and approve each week's digest before parents see it.</p>
          </div>
          <Button variant="primary" onClick={() => setShowGenForm(v => !v)} type="button">
            + Generate draft
          </Button>
        </div>

        {showGenForm && (
          <div className={styles.genForm}>
            <label className={styles.genLabel} htmlFor="gen-title">Unit title for new digest</label>
            <div className={styles.genRow}>
              <input
                id="gen-title"
                className={styles.genInput}
                value={genTitle}
                onChange={e => setGenTitle(e.target.value)}
                placeholder="e.g. Fractions"
                onKeyDown={e => e.key === 'Enter' && handleGenerate()}
              />
              <Button variant="primary" onClick={handleGenerate} loading={generating} type="button">
                Generate
              </Button>
              <Button variant="ghost" onClick={() => setShowGenForm(false)} type="button">Cancel</Button>
            </div>
            <p className={styles.genHint}>
              Claude will draft all sections from Year 2 curriculum data. You review before publishing.
            </p>
          </div>
        )}

        {digests.length === 0 ? (
          <div className={styles.empty}>
            <p>No digests yet. Generate your first one above.</p>
          </div>
        ) : (
          <div className={styles.cards}>
            {digests.map(digest => (
              <div key={digest.id} className={`${styles.card} ${styles[`status_${digest.status}`]}`}>
                <div
                  className={styles.cardHeader}
                  onClick={() => setExpanded(expanded === digest.id ? null : digest.id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={e => e.key === 'Enter' && setExpanded(expanded === digest.id ? null : digest.id)}
                  aria-expanded={expanded === digest.id}
                  aria-label={`${digest.unit_title} — click to ${expanded === digest.id ? 'collapse' : 'expand'}`}
                >
                  <div className={styles.cardMeta}>
                    <span className={styles.weekLabel}>
                      {TERM_LABELS[digest.term]} · Week {digest.week_number}
                    </span>
                    {digest.generated_by_ai && (
                      <span className={styles.aiTag}>AI draft</span>
                    )}
                  </div>
                  <div className={styles.cardTitleRow}>
                    <h2 className={styles.cardTitle}>{digest.unit_title}</h2>
                    <StatusBadge status={digest.status} />
                  </div>
                  <span className={styles.chevron}>{expanded === digest.id ? '▲' : '▼'}</span>
                </div>

                {expanded === digest.id && (
                  <div className={styles.cardBody}>
                    <InlineField label="Plain English" value={digest.plain_english} multiline
                      onSave={v => handleUpdate(digest.id, 'plain_english', v)} />
                    <InlineField label="In School" value={digest.in_school} multiline
                      onSave={v => handleUpdate(digest.id, 'in_school', v)} />
                    <InlineField label="Home Activity" value={digest.home_activity} multiline
                      onSave={v => handleUpdate(digest.id, 'home_activity', v)} />
                    <InlineField label="Times Table Tip" value={digest.times_table_tip}
                      onSave={v => handleUpdate(digest.id, 'times_table_tip', v)} />
                    <InlineField label="Teacher Note (optional)" value={digest.teacher_note || ''}
                      onSave={v => handleUpdate(digest.id, 'teacher_note', v || null as unknown as string)} />

                    <div className={styles.actions}>
                      {digest.status === 'draft' || digest.status === 'flagged' ? (
                        <Button variant="primary" onClick={() => handleApprove(digest.id)} type="button">
                          Approve
                        </Button>
                      ) : null}
                      {digest.status === 'approved' && (
                        <Button variant="primary" onClick={() => handlePublish(digest.id)} type="button">
                          Publish to parents
                        </Button>
                      )}
                      {digest.status === 'published' && (
                        <Button variant="secondary" onClick={() => handlePublish(digest.id)} type="button">
                          Re-publish
                        </Button>
                      )}
                      <span className={styles.timestamp}>
                        Updated {new Date(digest.updated_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}
                      </span>
                    </div>
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
