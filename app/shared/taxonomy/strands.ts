export const STRANDS = [
  'number-place-value',
  'number-addition-subtraction',
  'number-multiplication-division',
  'number-fractions',
  'number-decimals-percentages',
  'number-algebra',
  'measurement',
  'geometry-properties-of-shape',
  'geometry-position-direction',
  'statistics',
  'ratio-proportion',
] as const;

export type StrandId = (typeof STRANDS)[number];

export const STRAND_LABELS: Record<StrandId, string> = {
  'number-place-value': 'Number: Place Value',
  'number-addition-subtraction': 'Number: Addition and Subtraction',
  'number-multiplication-division': 'Number: Multiplication and Division',
  'number-fractions': 'Number: Fractions',
  'number-decimals-percentages': 'Number: Decimals and Percentages',
  'number-algebra': 'Number: Algebra',
  measurement: 'Measurement',
  'geometry-properties-of-shape': 'Geometry: Properties of Shape',
  'geometry-position-direction': 'Geometry: Position and Direction',
  statistics: 'Statistics',
  'ratio-proportion': 'Ratio and Proportion',
};

export const STRAND_VARIANTS: Record<StrandId, readonly string[]> = {
  'number-place-value': ['number place value', 'place value', 'number/place value'],
  'number-addition-subtraction': [
    'addition and subtraction',
    'number addition and subtraction',
    'calculation addition subtraction',
  ],
  'number-multiplication-division': [
    'multiplication and division',
    'number multiplication and division',
    'calculation multiplication division',
  ],
  'number-fractions': ['fractions', 'number fractions'],
  'number-decimals-percentages': ['decimals', 'percentages', 'decimals and percentages'],
  'number-algebra': ['algebra'],
  measurement: ['measurement', 'measures'],
  'geometry-properties-of-shape': ['geometry properties of shape', 'shape', 'properties of shape'],
  'geometry-position-direction': ['geometry position and direction', 'position and direction'],
  statistics: ['statistics', 'data handling'],
  'ratio-proportion': ['ratio', 'proportion', 'ratio and proportion'],
};
