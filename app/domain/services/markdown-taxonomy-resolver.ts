import {
  resolveStrandId,
  resolveWhiteRoseBlockId,
  resolveWhiteRoseTermId,
  resolveYearGroupId,
  type CanonicalTaxonomyIds,
} from '../../shared/taxonomy';

export interface MarkdownTaxonomyInput {
  yearGroupLabel: string;
  strandLabel: string;
  termLabel?: string;
  blockLabel?: string;
}

export function resolveMarkdownTaxonomy(input: MarkdownTaxonomyInput): CanonicalTaxonomyIds {
  const yearGroupId = resolveYearGroupId(input.yearGroupLabel);
  if (!yearGroupId) {
    throw new Error(`Unrecognized year group label: ${input.yearGroupLabel}`);
  }

  const strandId = resolveStrandId(input.strandLabel);
  if (!strandId) {
    throw new Error(`Unrecognized strand label: ${input.strandLabel}`);
  }

  const termId = input.termLabel ? resolveWhiteRoseTermId(input.termLabel) : undefined;
  if (input.termLabel && !termId) {
    throw new Error(`Unrecognized White Rose term label: ${input.termLabel}`);
  }

  const blockId = input.blockLabel ? resolveWhiteRoseBlockId(input.blockLabel) : undefined;
  if (input.blockLabel && !blockId) {
    throw new Error(`Unrecognized White Rose block label: ${input.blockLabel}`);
  }

  return {
    yearGroupId,
    strandId,
    termId,
    blockId,
  };
}
