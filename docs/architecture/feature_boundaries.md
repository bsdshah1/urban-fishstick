# Feature Boundaries

## Purpose
This document defines module ownership, contracts, and dependencies so features stay decoupled from raw curriculum files (`context_docs*`) and depend on domain services instead.

## Design Principles
- **Feature modules orchestrate workflows** and own request/response shapes.
- **Domain services own data access/normalization** from source documents and persistence.
- **Features never read files directly** (no direct parsing of `brainstorm.md`, `context_docs/*.pdf`, or `context_docs_md/*.md`).
- **Cross-feature reuse happens through domain contracts**, not imports between feature internals.

## Module Scope and Dependencies

### `app/domain`
**Scope**
- Canonical interfaces for curriculum data, times-table progress, and parent-facing explanation generation.
- Shared domain DTOs and service protocols.

**Inputs**
- Normalized queries from feature modules.

**Outputs**
- Structured domain records (units, methods, progress state, parent explanations).

**Dependencies**
- Infrastructure adapters (file loaders, databases, vector stores, etc.).

---

### `app/features/lesson_planner`
**Scope**
- Build differentiated lesson plans using CPA flow and curriculum sequencing.

**Input contract**
- `LessonPlannerRequest` (year group, block, objective, differentiation profile).

**Output contract**
- `LessonPlannerResponse` with lesson phases, suggested activities, vocabulary focus, and references.

**Dependencies**
- `CurriculumDomainService` (for mapped White Rose small steps and progression).
- `LessonContentService` (for activity templates and worked examples).

---

### `app/features/times_table_tracker`
**Scope**
- Track pupil progression against EYFS–Y6 times-table expectations.

**Input contract**
- `TimesTableTrackerRequest` (pupil id, cohort/year, optional assessment event).

**Output contract**
- `TimesTableTrackerResponse` with mastered facts, current focus tables, and next-step practice plan.

**Dependencies**
- `TimesTableProgressService` (retrieve/update mastery states).
- `CurriculumDomainService` (year expectations and progression metadata).

---

### `app/features/parent_explainer`
**Scope**
- Generate jargon-light, policy-aligned parent explainers for taught methods.

**Input contract**
- `ParentExplainerRequest` (year group, operation/topic, reading level, optional locale).

**Output contract**
- `ParentExplainerResponse` with summary, worked method steps, common misconceptions, and home-practice tips.

**Dependencies**
- `CalculationMethodService` (approved methods by year/operation).
- `ParentCommunicationService` (tone/style constraints, translation/reading-level transformations).

## MVP Feature Set
Recommended MVP (implemented first):
1. **Lesson Planner**
2. **Times-Table Tracker**
3. **Parent Explainer**

These three features provide immediate classroom planning value, pupil progress visibility, and home-school communication support.

## Non-MVP Backlog (from `brainstorm.md`)
Deferred items after MVP:
- Vocabulary Wall Generator
- CPA Resource Recommender
- Reasoning & Problem-Solving Bank
- Gap Analysis Tool
- Progression Snapshot Cards
- Calculation Policy Quick-Reference
- Lesson Observation Checklist
- Quick wins:
  - Printable times table focus card per year group
  - Half-termly vocabulary list exports by year group
  - “What comes next?” progression prompts for teachers moving between units
- Bigger bets:
  - AI tutor for mastery-style questioning
  - Whole-school data dashboard aligned to White Rose small steps

## Dependency Rules
- `app/features/*` may import only:
  - their local `contracts.py`
  - shared types in `app/domain/services.py`
- `app/features/*` must **not** import:
  - raw files under `context_docs/` or `context_docs_md/`
  - parsing/loading utilities from infrastructure layers
- Infrastructure adapters implement domain protocols and are injected at runtime.

## Integration Pattern
1. Feature receives request DTO.
2. Feature calls domain service protocol(s).
3. Feature composes a response DTO.
4. API/CLI/UI layers serialize response.

This keeps feature logic testable and stable even if source documents or storage adapters change.
