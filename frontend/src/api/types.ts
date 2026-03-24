export type DigestStatus = 'draft' | 'approved' | 'published' | 'flagged'
export type UserRole = 'parent' | 'teacher' | 'admin'

export interface VocabEntry {
  term: string
  definition: string
}

export interface Digest {
  id: number
  year_group: string
  term: string
  week_number: number
  unit_title: string
  status: DigestStatus
  plain_english: string
  in_school: string
  home_activity: string
  dinner_table_questions: string[]
  key_vocabulary: VocabEntry[]
  example_questions: string[]
  times_table_tip: string
  teacher_note: string | null
  generated_by_ai: boolean
  created_at: string
  updated_at: string
  approved_at: string | null
  published_at: string | null
  approved_by_id: number | null
}

export interface User {
  id: number
  email: string
  name: string
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface DigestUpdate {
  plain_english?: string
  in_school?: string
  home_activity?: string
  dinner_table_questions?: string[]
  key_vocabulary?: VocabEntry[]
  example_questions?: string[]
  times_table_tip?: string
  teacher_note?: string | null
  unit_title?: string
}

export interface GenerateRequest {
  year_group: string
  term: string
  week_number: number
  unit_title: string
}

export interface Settings {
  school_name: string
  active_year_groups: string[]
  current_term: string
  current_week: number
}
