import type { ReactNode } from 'react'
import styles from './SectionCard.module.css'

interface Props {
  title: string
  accent?: boolean
  children: ReactNode
}

export function SectionCard({ title, accent, children }: Props) {
  return (
    <section className={`${styles.card} ${accent ? styles.accent : ''}`}>
      <h2 className={styles.title}>{title}</h2>
      <div className={styles.body}>{children}</div>
    </section>
  )
}
