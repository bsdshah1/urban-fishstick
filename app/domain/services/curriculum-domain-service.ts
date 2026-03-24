import type { CanonicalTaxonomyIds } from '../../shared/taxonomy';

export interface CurriculumItem {
  id: string;
  title: string;
  taxonomy: CanonicalTaxonomyIds;
}

/**
 * Domain service now consumes canonical taxonomy IDs only.
 * Callers should resolve markdown/raw labels before invoking this service.
 */
export function buildCurriculumItem(input: {
  id: string;
  title: string;
  taxonomy: CanonicalTaxonomyIds;
}): CurriculumItem {
  return {
    id: input.id,
    title: input.title,
    taxonomy: input.taxonomy,
  };
}
