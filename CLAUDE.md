# Pik Nirnay — Claude Code Instructions

## 1. Project Purpose

Pik Nirnay is a Marathi-first pre-sowing climate and financial risk decision-support prototype for rain-fed farmers, initially focused on Dharashiv district, Maharashtra.

The product does **not** attempt to predict a single “best crop.”

Its purpose is to compare a small set of realistic crop or cropping-system options using:

- soil type / soil depth
- sowing date
- irrigation availability
- current and historical weather conditions
- drought and excess-rain risk
- approximate input exposure
- historical market-price behaviour
- documented agronomic contingency rules

The output should help the user understand:

- what options are feasible
- what risks exist for each option
- what assumptions drove the result
- why a particular option is classified as lower or higher risk

## 2. Current Product Boundary

V1 is intentionally narrow.

Initial scope:

- Geography: Dharashiv district
- Season: Kharif
- User: rain-fed or limited-irrigation farmer
- Language: Marathi first, English supported
- Decision model: explainable deterministic / scenario-based rules
- Architecture: modular monolith
- Backend: FastAPI
- Database: PostgreSQL / PostGIS where appropriate
- Frontend: lightweight responsive web application / PWA
- External data: approved weather, climate and market-data providers

Do not expand scope without explicit approval.

## 3. Non-Goals for V1

Do not introduce the following unless explicitly requested:

- generic agricultural chatbot
- fertilizer or pesticide marketplace
- crop disease diagnosis
- lending
- insurance claims
- farmer social network
- satellite-based crop monitoring
- IoT integration
- machine-learning-based crop recommendation
- microservices
- Kafka or event streaming
- Kubernetes
- complex cloud infrastructure
- unnecessary AI agents inside the product

Pik Nirnay itself is not being built as an “AI product.”

AI may later be used for language interaction or explanation, but it must not silently replace documented agronomic decision logic.

## 4. Source of Truth

Before implementing a feature, read the relevant documents.

Priority order:

1. `docs/product/PRD.md`
2. Relevant architecture/design document
3. Relevant ADR
4. Relevant research / evidence document
5. Existing code and tests
6. Task-specific instructions

If documents conflict, do not silently choose one. Report the conflict.

## 5. Domain Rules Are Controlled Requirements

Agricultural rules must not be invented from general knowledge.

Every agronomic rule must originate from:

- documented research
- government / university / agricultural institution guidance
- approved project research
- an explicitly accepted product assumption

Never create or modify an agricultural rule simply because it seems reasonable.

If a required domain rule is missing, flag it as a blocker or assumption.

## 6. Separate Domain Truth from Software Truth

Always distinguish:

### Domain truth

Is the agricultural or financial rule itself valid and supported?

### Software truth

Has the approved rule been implemented correctly?

Claude Code is responsible for software truth.

Do not assume successful implementation proves domain validity.

## 7. Working Method

For any non-trivial task, use:

**Understand → Plan → Decompose → Execute → Verify → Review**

Follow the detailed protocol in:

`docs/agentic-task-protocol.md`

Do not begin implementation immediately after reading the task unless it is trivial.

## 8. Scope Discipline

Every task must have a bounded objective.

Do not:

- refactor unrelated code
- redesign architecture without need
- introduce new frameworks without justification
- expand feature scope while implementing
- change product behaviour outside the task
- make speculative improvements merely because they are interesting

Prefer the smallest change that satisfies the requirement cleanly.

## 9. Architecture Principles

Default to:

- modular monolith
- clear module boundaries
- provider abstractions for external dependencies
- explicit contracts between modules
- simple synchronous flows unless asynchronous processing is genuinely needed
- configuration over hard-coded provider behaviour
- explainability over opaque scoring
- observability where useful
- graceful degradation when external services fail

Avoid premature distribution.

## 10. External Data Providers

External provider-specific structures must not leak directly into domain logic.

Use adapters / provider interfaces.

Example:

```text
WeatherProvider
    ├── OpenMeteoProvider
    ├── NasaPowerProvider
    └── ImdProvider
```

Normalize provider responses before they reach the decision engine.

The decision engine should depend on project-owned domain contracts rather than third-party schemas.

## 11. Decision Engine Principles

The decision engine must remain explainable.

Every decision output should be traceable to:

- user input
- weather / climate information
- market information
- rule versions
- data timestamps
- applicable agronomic rules

Avoid unexplained composite scores.

If a risk category such as LOW / MEDIUM / HIGH is calculated, the contributing conditions must be inspectable.

## 12. Marathi-First Requirement

Marathi is a first-class product language.

Do not design English text first and mechanically translate it later.

Use localization keys.

Example:

```text
risk.low
risk.medium
risk.high
soil.shallow_black
soil.medium_black
soil.deep_black
```

Language files should remain separate from business logic.

Avoid hard-coded user-facing text.

## 13. Data Provenance

Where relevant, retain:

- source
- provider
- fetched-at timestamp
- effective date
- dataset version
- rule version

A user or developer should be able to understand where important information originated.

## 14. Testing Expectations

Every meaningful implementation should include appropriate tests.

Depending on the change:

- unit tests
- domain/rule tests
- provider adapter tests
- API tests
- integration tests
- historical scenario/replay tests

Decision rules should be especially well covered.

Prefer deterministic tests.

## 15. Verification Loop

Do not consider a task finished merely because code compiles.

Before reporting completion:

1. run relevant tests
2. inspect failures
3. fix issues
4. rerun tests
5. compare output against acceptance criteria
6. review the code for unintended scope changes
7. update relevant documentation if behaviour changed

If verification cannot be completed, say exactly what remains unverified.

## 16. Documentation

Update documentation when a change alters:

- architecture
- interfaces
- product behaviour
- decision rules
- data sources
- assumptions
- setup instructions

Do not duplicate the same detailed information across many documents.

Prefer linking to the authoritative source.

## 17. ADR Usage

Create an Architecture Decision Record when making a meaningful structural decision such as:

- changing database technology
- introducing asynchronous processing
- introducing a new external data provider
- introducing a new architectural layer
- changing deployment topology
- moving from modular monolith to distributed services

Do not create ADRs for routine implementation details.

## 18. Security and Safety

Do not expose:

- credentials
- API keys
- secrets
- internal tokens

Validate external input.

Treat third-party responses as untrusted data.

This application provides decision support, not guaranteed agricultural outcomes.

Do not introduce wording that claims certainty where uncertainty exists.

## 19. Definition of Done

A task is complete only when:

- requested behaviour is implemented
- acceptance criteria are met
- relevant tests pass
- code stays within scope
- domain rules match approved specifications
- user-facing strings are localized where applicable
- provenance/explainability requirements are preserved
- relevant documentation is updated
- unresolved issues are explicitly reported

## 20. When Unsure

Do not guess about:

- agricultural rules
- product scope
- risk interpretation
- financial assumptions
- architecture decisions with long-term impact

Record the uncertainty and ask for a product/domain decision before embedding the assumption permanently in the system.
