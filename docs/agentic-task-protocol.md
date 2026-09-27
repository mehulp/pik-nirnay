# Pik Nirnay — Agentic Task Protocol

## 1. Purpose

This document defines how implementation work should be performed using an **Agent → Loop → Graph** methodology.

The objective is not to make development unnecessarily complex.

The objective is to ensure that AI-assisted implementation remains:

- bounded
- traceable
- testable
- reviewable
- aligned with product requirements
- safe from uncontrolled architectural drift

## 2. Core Model

### Agent

An agent is:

**Goal + Context + Tools + State + Exit Criteria**

An agent should always know:

- what problem it is solving
- what information it may use
- what tools it may use
- what state or files it may modify
- how success will be measured
- when it should stop

Avoid vague instructions such as:

> Improve the project.

Prefer:

> Implement the Open-Meteo adapter according to the WeatherProvider contract and satisfy the listed acceptance criteria.

## 3. The Execution Loop

Every meaningful task should follow:

```text
UNDERSTAND
    ↓
PLAN
    ↓
EXECUTE
    ↓
VERIFY
    ↓
REVIEW
    ↓
PASS?
 ┌──┴───┐
 NO     YES
 ↓       ↓
FIX     STOP
 └──→ LOOP
```

## 4. Step 1 — Understand

Before modifying code:

1. Read the task.
2. Read relevant requirements.
3. Inspect relevant architecture documentation.
4. Inspect the existing implementation.
5. Identify dependencies.
6. Identify relevant tests.
7. Identify unknowns or contradictions.

Create a short task summary:

```text
Goal:
What must change?

Current state:
How does the system behave now?

Constraints:
What must not change?

Dependencies:
What other modules or providers are involved?

Acceptance criteria:
How will completion be verified?
```

Do not start implementation until the intended behaviour is clear.

## 5. Step 2 — Plan

Create a bounded implementation plan.

Example:

```text
1. Define normalized weather DTO.
2. Define WeatherProvider interface.
3. Implement OpenMeteoProvider.
4. Add error mapping.
5. Add unit tests.
6. Add mocked integration test.
7. Update architecture documentation.
```

The plan should represent implementation work, not speculative future features.

## 6. Step 3 — Decide Whether a Graph Is Needed

Not every task requires a graph.

Use a simple sequential loop when:

- change is isolated
- only one module is involved
- dependencies are linear
- the work is small

Use a task graph when:

- several independent investigations are needed
- multiple modules can progress independently
- implementation depends on several prerequisites
- review can be separated from implementation
- external-provider work can be isolated
- the task is large enough that dependency ordering matters

## 7. Graph Representation

Represent substantial work as nodes with explicit dependencies.

Example:

```text
                    Weather Integration
                           │
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
       Inspect API     Inspect domain   Inspect tests
             │             │             │
             └─────────────┼─────────────┘
                           ↓
                 Define normalized model
                           ↓
                 Define provider contract
                           ↓
                    Implement adapter
                           ↓
                    Add test coverage
                           ↓
                    Independent review
                           ↓
                        Complete
```

Every node should have a clear output.

## 8. Parallelism

Parallel work is useful only when nodes are genuinely independent.

Good candidates:

```text
External API research
        +
Existing code inspection
        +
Test strategy analysis
```

Poor candidates:

```text
Define contract
        +
Implement contract consumer
```

when the consumer depends on the contract design.

Do not parallelize work merely to make the process look agentic.

## 9. Node Contract

Each graph node should define:

```text
Node:
Weather provider contract

Goal:
Define the internal weather abstraction.

Inputs:
PRD, architecture docs, existing domain models.

Output:
Interface + normalized data contract.

Allowed changes:
Weather module only.

Dependencies:
None.

Verification:
Contract supports current forecast and historical-data requirements.

Exit criteria:
Interface reviewed and tests compile.
```

This keeps execution bounded.

## 10. Implementation Agents

Implementation agents should make focused changes.

They may:

- inspect code
- modify code
- add tests
- add migrations
- update documentation
- run commands
- fix failures related to their task

They should not:

- widen the task
- redefine product requirements
- rewrite unrelated modules
- modify agricultural rules
- introduce new architecture without approval

## 11. Reviewer Agent

For important changes, perform a review pass separate from implementation.

The reviewer should inspect:

- correctness
- acceptance-criteria coverage
- architecture consistency
- unintended scope changes
- test quality
- rule traceability
- localization impact
- error handling
- provenance
- security

The reviewer should actively look for faults rather than confirm the implementer's assumptions.

## 12. Domain Reviewer

Agricultural decision logic receives an additional review category.

For every new or changed rule, verify:

```text
Rule ID:
R-DHAR-KH-001

Source:
Approved research / contingency plan / evidence register.

Condition:
Shallow black soil + rain-fed + delayed sowing beyond X.

Outcome:
Allowed / discouraged / alternative cropping system.

Implementation test:
Scenario produces expected classification.
```

Software review validates implementation.

Human/product/domain review validates whether the rule itself should exist.

## 13. Decision-Rule Versioning

Decision rules should be versionable.

Avoid burying critical agricultural behaviour across arbitrary `if/else` statements.

Prefer structured configuration or explicit domain rules where feasible.

Conceptually:

```text
rule_id
version
source
conditions
outcome
explanation_key
effective_from
status
```

Changing a significant rule should be traceable.

## 14. Verification Loop

After implementation:

### Functional verification

Confirm requested behaviour works.

### Test verification

Run relevant automated tests.

### Requirement verification

Compare implementation with acceptance criteria.

### Architecture verification

Check that module boundaries remain intact.

### Domain verification

Confirm approved rules were implemented exactly.

### Documentation verification

Check whether documentation requires updates.

If anything fails:

```text
Failure
   ↓
Diagnose
   ↓
Fix
   ↓
Rerun verification
```

Repeat until pass or blocker.

## 15. Failure Classification

Failures should be classified before fixing.

Use categories such as:

```text
IMPLEMENTATION_ERROR
TEST_ERROR
REQUIREMENT_AMBIGUITY
DOMAIN_RULE_GAP
PROVIDER_FAILURE
DATA_QUALITY_FAILURE
ARCHITECTURE_CONFLICT
ENVIRONMENT_FAILURE
```

This prevents code changes from being used to hide requirement or domain problems.

## 16. External Provider Failure

External providers must be treated as unreliable.

Possible failures include:

- timeout
- authentication failure
- malformed response
- quota exceeded
- missing data
- stale data
- service outage

Provider failures should not automatically become decision-engine failures.

Where possible:

```text
Provider
   ↓
Adapter
   ↓
Validation
   ↓
Normalized domain data
```

Invalid provider data must be rejected or marked unavailable.

## 17. Historical Replay as a Verification Agent

Pik Nirnay has a useful domain-specific verification mechanism:

**historical replay.**

Example:

```text
Input:
Dharashiv
Shallow black soil
Rain-fed
10 July 2023

Historical weather:
Actual rainfall sequence from Kharif 2023.

Engine:
Run rules using only information that would have been available at that date.

Output:
Crop-risk cards.

Review:
Would these classifications have been reasonable?
```

Historical replay is not proof of future performance.

It is a sanity-check mechanism.

## 18. Explainability Verification

Every risk output should answer:

> Why did I receive this result?

Example:

```text
Risk: HIGH

Reasons:
- shallow black soil
- no protective irrigation
- sowing date later than preferred window
- high sensitivity to prolonged dry spell

Sources:
- rule R-DHAR-KH-014
- weather snapshot W-2026-07-10
```

If a risk label cannot be explained from stored inputs/rules, the implementation is incomplete.

## 19. Localization Verification

For every user-facing feature, check:

- Marathi translation exists
- English translation exists
- no business logic depends on translated text
- text fits expected UI context
- numbers and units remain understandable
- agricultural terminology uses approved Marathi wording

Localization failures should not alter business behaviour.

## 20. Example Task Workflow — Weather

Task:

> Add Open-Meteo weather support.

Graph:

```text
                  Open-Meteo Integration
                          │
          ┌───────────────┼────────────────┐
          ↓               ↓                ↓
    API analysis    Existing weather   Test inspection
                         model
          │               │                │
          └───────────────┼────────────────┘
                          ↓
              Define WeatherProvider
                          ↓
              Define normalized DTO
                          ↓
             Implement OpenMeteoProvider
                          ↓
                    Add tests
                          ↓
                 Failure scenarios
                          ↓
                  Reviewer pass
                          ↓
                       DONE
```

Acceptance criteria:

```text
- provider returns normalized forecast data
- external schema does not leak into domain layer
- timeout produces controlled provider error
- missing rainfall data is handled explicitly
- unit tests pass
- mocked provider integration test passes
- architecture documentation updated
```

## 21. Example Decision-Engine Task

Task:

> Implement delayed-sowing rules for shallow black soil.

Required inputs:

```text
- approved rule matrix
- rule IDs
- source references
- expected Marathi explanation strings
- defined risk outcomes
```

Graph:

```text
Approved rule matrix
        ↓
Rule model
        ↓
Implementation
        ↓
Scenario tests
        ↓
Historical replay
        ↓
Reviewer
        ↓
Done
```

Claude must not fill gaps in the matrix from general agricultural knowledge.

## 22. Human Decision Gates

Some graph nodes must stop for a human decision.

Typical gates:

```text
DOMAIN_RULE_APPROVAL
PRODUCT_SCOPE_CHANGE
ARCHITECTURE_CHANGE
NEW_EXTERNAL_DEPENDENCY
MATERIAL_COST_INCREASE
USER_SAFETY_IMPACT
```

At a gate, document:

- decision needed
- alternatives
- trade-offs
- recommended technical interpretation if appropriate

Do not silently proceed.

## 23. Task Handoff Format

When Claude completes a task, report:

```text
TASK
<name>

IMPLEMENTED
- ...
- ...

FILES CHANGED
- ...
- ...

TESTS
- ...

VERIFICATION
- ...

ASSUMPTIONS
- ...

UNRESOLVED
- ...

DOCUMENTATION
- ...

NEXT DEPENDENCY
- ...
```

Keep the report factual.

Do not report “complete” when verification is partial.

## 24. Project-Level Loop

The entire Pik Nirnay project follows a larger loop:

```text
Research
   ↓
Evidence
   ↓
Product decision
   ↓
Requirement
   ↓
Architecture / design
   ↓
Claude implementation task
   ↓
Implementation
   ↓
Verification
   ↓
Historical replay
   ↓
Review
   ↓
Learning
   ↓
PRD / design refinement
   ↓
Next iteration
```

New evidence may change old assumptions.

Changing an assumption should trigger review of dependent rules.

## 25. Dependency Graph Principle

Requirements should flow downstream.

```text
Evidence
   ↓
Domain rule
   ↓
Decision-engine behaviour
   ↓
API contract
   ↓
UX explanation
   ↓
Tests
```

Do not reverse this sequence.

For example, do not design a convenient UI scoring system and then invent agronomic rules to justify it.

## 26. Simplicity Principle

Agents, loops and graphs are coordination methods.

They are **not product architecture requirements**.

Do not introduce:

- agent frameworks
- LangGraph
- message brokers
- orchestration systems
- queues
- distributed workers

merely because the development process uses agentic methodology.

Use the methodology to build a simple product well.

## 27. Definition of a Successful Agentic Task

A task is successful when:

- objective was bounded
- prerequisites were understood
- dependencies were respected
- approved rules were followed
- implementation passed verification
- reviewer found no unresolved critical issue
- documentation remains consistent
- next dependency is clear

Success is measured by verified output, not by amount of generated code.
