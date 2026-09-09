# ReadRight

**Every Child. Every Learner. Every Future.**

ReadRight is a Learning Intelligence Infrastructure platform that turns learner evidence into an actionable learning picture for teachers.

Core loop:

`Evidence -> Understanding -> Action -> Verification -> Updated Learner State`

Teacher experience:

`WHY -> DO -> VERIFY`

## Architecture

- `apps/web` - Next.js + TypeScript teacher and child product
- `backend/readright` - FastAPI scientific and assessment engine
- `packages/design-system` - ReadRight visual system and shared UI primitives
- `packages/task-schema` - shared task/evidence contracts
- `content` - versioned task banks and intervention content
- `docs` - product, science, design and governance specifications
- `tests` - cross-system test fixtures and scenarios
- `infra` - deployment and local infrastructure

## Engineering principles

1. Evidence is immutable.
2. Observation is stored separately from inference.
3. The generative AI layer cannot write learner state.
4. Experimental signals cannot independently determine learner state.
5. The engine may return `INSUFFICIENT_EVIDENCE` instead of forcing a conclusion.
6. Every scientific decision is versioned and auditable.
7. Child-facing assessment stays focused, accessible and low-distraction.
8. Sensitive learner data never goes to general product analytics.

This repository is the clean foundation for the new ReadRight platform.
