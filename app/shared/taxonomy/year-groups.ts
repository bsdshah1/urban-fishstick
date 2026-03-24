export const YEAR_GROUPS = [
  'eyfs',
  'y1',
  'y2',
  'y3',
  'y4',
  'y5',
  'y6',
] as const;

export type YearGroupId = (typeof YEAR_GROUPS)[number];

export const YEAR_GROUP_LABELS: Record<YearGroupId, string> = {
  eyfs: 'EYFS',
  y1: 'Year 1',
  y2: 'Year 2',
  y3: 'Year 3',
  y4: 'Year 4',
  y5: 'Year 5',
  y6: 'Year 6',
};

export const YEAR_GROUP_VARIANTS: Record<YearGroupId, readonly string[]> = {
  eyfs: ['eyfs', 'early years', 'reception', 'foundation stage', 'fs2'],
  y1: ['year 1', 'y1', 'ks1 year 1', 'year one'],
  y2: ['year 2', 'y2', 'ks1 year 2', 'year two'],
  y3: ['year 3', 'y3', 'lks2 year 3', 'year three'],
  y4: ['year 4', 'y4', 'lks2 year 4', 'year four'],
  y5: ['year 5', 'y5', 'uks2 year 5', 'year five'],
  y6: ['year 6', 'y6', 'uks2 year 6', 'year six'],
};
