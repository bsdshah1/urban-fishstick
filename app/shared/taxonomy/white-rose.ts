export const WHITE_ROSE_TERMS = ['autumn', 'spring', 'summer'] as const;

export type WhiteRoseTermId = (typeof WHITE_ROSE_TERMS)[number];

export const WHITE_ROSE_TERM_LABELS: Record<WhiteRoseTermId, string> = {
  autumn: 'Autumn',
  spring: 'Spring',
  summer: 'Summer',
};

export const WHITE_ROSE_TERM_VARIANTS: Record<WhiteRoseTermId, readonly string[]> = {
  autumn: ['autumn', 'autumn term', 'autumn 1', 'autumn 2', 'fall'],
  spring: ['spring', 'spring term', 'spring 1', 'spring 2'],
  summer: ['summer', 'summer term', 'summer 1', 'summer 2'],
};

export const WHITE_ROSE_BLOCKS = [
  'place-value',
  'addition-subtraction',
  'multiplication-division',
  'fractions',
  'decimals',
  'percentages',
  'geometry',
  'position-direction',
  'measurement',
  'statistics',
  'ratio',
  'algebra',
] as const;

export type WhiteRoseBlockId = (typeof WHITE_ROSE_BLOCKS)[number];

export const WHITE_ROSE_BLOCK_LABELS: Record<WhiteRoseBlockId, string> = {
  'place-value': 'Place Value',
  'addition-subtraction': 'Addition and Subtraction',
  'multiplication-division': 'Multiplication and Division',
  fractions: 'Fractions',
  decimals: 'Decimals',
  percentages: 'Percentages',
  geometry: 'Geometry',
  'position-direction': 'Position and Direction',
  measurement: 'Measurement',
  statistics: 'Statistics',
  ratio: 'Ratio',
  algebra: 'Algebra',
};

export const WHITE_ROSE_BLOCK_VARIANTS: Record<WhiteRoseBlockId, readonly string[]> = {
  'place-value': ['place value', 'number place value'],
  'addition-subtraction': ['addition and subtraction', 'add/subtract'],
  'multiplication-division': ['multiplication and division', 'multiply/divide'],
  fractions: ['fractions'],
  decimals: ['decimals'],
  percentages: ['percentages', 'percent'],
  geometry: ['geometry', 'properties of shape'],
  'position-direction': ['position and direction'],
  measurement: ['measurement'],
  statistics: ['statistics'],
  ratio: ['ratio', 'ratio and proportion'],
  algebra: ['algebra'],
};
