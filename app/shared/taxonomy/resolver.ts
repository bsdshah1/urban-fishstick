import { STRANDS, STRAND_VARIANTS, type StrandId } from './strands';
import {
  WHITE_ROSE_BLOCKS,
  WHITE_ROSE_BLOCK_VARIANTS,
  WHITE_ROSE_TERMS,
  WHITE_ROSE_TERM_VARIANTS,
  type WhiteRoseBlockId,
  type WhiteRoseTermId,
} from './white-rose';
import { YEAR_GROUPS, YEAR_GROUP_VARIANTS, type YearGroupId } from './year-groups';

function normalize(label: string): string {
  return label
    .trim()
    .toLowerCase()
    .replace(/[–—]/g, '-')
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, ' ');
}

function resolveFromMap<TId extends string>(
  value: string,
  ids: readonly TId[],
  variants: Record<TId, readonly string[]>,
): TId | null {
  const normalizedInput = normalize(value);

  for (const id of ids) {
    if (id === normalizedInput) {
      return id;
    }

    const normalizedVariants = variants[id].map(normalize);
    if (normalizedVariants.includes(normalizedInput)) {
      return id;
    }
  }

  return null;
}

export interface CanonicalTaxonomyIds {
  yearGroupId: YearGroupId;
  strandId: StrandId;
  termId?: WhiteRoseTermId;
  blockId?: WhiteRoseBlockId;
}

export function resolveYearGroupId(value: string): YearGroupId | null {
  return resolveFromMap(value, YEAR_GROUPS, YEAR_GROUP_VARIANTS);
}

export function resolveStrandId(value: string): StrandId | null {
  return resolveFromMap(value, STRANDS, STRAND_VARIANTS);
}

export function resolveWhiteRoseTermId(value: string): WhiteRoseTermId | null {
  return resolveFromMap(value, WHITE_ROSE_TERMS, WHITE_ROSE_TERM_VARIANTS);
}

export function resolveWhiteRoseBlockId(value: string): WhiteRoseBlockId | null {
  return resolveFromMap(value, WHITE_ROSE_BLOCKS, WHITE_ROSE_BLOCK_VARIANTS);
}
