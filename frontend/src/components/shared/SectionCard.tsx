import type { ReactNode } from 'react'
import styles from './SectionCard.module.css'

interface Props {
  category: string
  subtitle: string
  icon: ReactNode
  accent?: boolean
  children: ReactNode
}

export function SectionCard({ category, subtitle, icon, accent, children }: Props) {
  return (
    <section className={`${styles.card} ${accent ? styles.accent : ''}`}>
      <div className={styles.header}>
        <div className={styles.iconBox} aria-hidden="true">{icon}</div>
        <div className={styles.headerText}>
          <span className={styles.category}>{category}</span>
          <span className={styles.subtitle}>{subtitle}</span>
        </div>
      </div>
      <div className={styles.body}>{children}</div>
    </section>
  )
}
