import { useEffect } from 'react'
import styles from './Toast.module.css'

export type ToastType = 'success' | 'warning' | 'error'

interface Props {
  message: string
  type?: ToastType
  onDismiss: () => void
  duration?: number
}

export function Toast({ message, type = 'success', onDismiss, duration = 3000 }: Props) {
  useEffect(() => {
    const t = setTimeout(onDismiss, duration)
    return () => clearTimeout(t)
  }, [onDismiss, duration])

  return (
    <div className={`${styles.toast} ${styles[type]}`} role="status" aria-live="polite">
      {message}
      <button className={styles.close} onClick={onDismiss} aria-label="Dismiss">×</button>
    </div>
  )
}
