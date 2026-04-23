# STAIR Assessment Instrument v1.0

> **⚠ INSTRUMENT PREAMBLE INCONSISTENCY — READ BEFORE USING**
>
> The preamble of this document says "32 scoreable sub-dimensions." This is wrong. The actual scoring in `data/moodle_scores.json` uses **28 sub-dimensions** (L1:5, L2:6, L3:7, L4:5, L5:5). The per-level counts in this document (L3:6, L4:7, L5:8) also differ from the scored data — this was an earlier instrument draft.
>
> **Canonical sub-dimension count: 28.** See `data/moodle_scores.json` for the definitive list of all 28 scored sub-dimensions.
>
> The rubric criteria, evidence hierarchy, and scoring logic in this document remain valid and were applied during the Moodle evaluation.

## Formal Scoring Rubric for Platform Readiness Evaluation

**Framework:** STAIR (Scaffold for Teaching Agent Reasoning Readiness)
**Version:** 1.0
**Author:** Baqar Jafri, University of Stirling
**Date:** March 2026
**Purpose:** Standardized, reproducible assessment of learning platform architectural readiness for AI teaching Agent Reasoning

---

## Part A: Instrument Overview

### A1. Purpose and Scope

This instrument provides a formal, reproducible method for evaluating whether a learning management system (LMS) possesses the architectural capabilities required to host autonomous AI teaching agents. It operationalizes the STAIR framework's five levels into 32 scoreable sub-dimensions, each with explicit criteria anchored to observable evidence.

The instrument is designed for:
- **Researchers** evaluating platform readiness across different LMS platforms
- **Platform developers** identifying specific architectural gaps
- **Practitioners** making informed adoption decisions
- **Reviewers** assessing the rigor of STAIR-based evaluations

### A2. Theoretical Grounding

Each sub-dimension is grounded in one or more of three theoretical frameworks:

| Code | Framework | Domain |
|------|-----------|--------|
| **Z** | Zimmerman (2002) — Self-Regulated Learning | What learners need from scaffolding systems |
| **T** | Talebirad & Nadiri (2023) — Agentic AI Taxonomy | What agents need from their environment |
| **H** | Chu et al. (2025, EMNLP) — LLM Agents for Education | What educational AI specifically requires |

Sub-dimensions grounded in all three frameworks (marked Z+T+H) represent the strongest convergence points and are candidates for priority weighting in sensitivity analysis.

### A3. Relationship to Existing Maturity Models

| Model | Domain | Relationship to STAIR |
|-------|--------|----------------------|
| **CMM/CMMI** | Software process maturity | Analogous structure (ordinal levels, defined criteria). STAIR assesses platform *architecture*, not organizational *process*. |
| **TRL** (Technology Readiness Levels) | Technology maturation | Complementary. TRL assesses an agent's maturity (concept to deployment); STAIR assesses the *platform's* readiness to host that agent. An agent at TRL 6 still needs a STAIR L3+ platform. |
| **SAMR** (Puentedura, 2006) | Technology integration in teaching | Different axis. SAMR describes how technology transforms *pedagogy*; STAIR describes whether *architecture* can support AI agents. SAMR is pedagogical; STAIR is architectural. |
| **TPACK** (Mishra & Koehler, 2006) | Teacher knowledge for tech integration | Different scope. TPACK addresses teacher capability; STAIR addresses platform capability. Both are needed for successful agent deployment. |

**Novel contribution:** No existing maturity model specifically addresses platform readiness for autonomous AI teaching agents. STAIR fills this gap by combining learning science (what agents should do), AI systems engineering (what agents need), and educational AI research (what platforms must enable).

### A4. Assessor Qualifications

Assessors should possess:
- Ability to read and navigate source code in the platform's primary language (e.g., PHP for Moodle, Python for Open edX)
- Familiarity with LMS architecture concepts (events, APIs, plugins, authentication)
- Understanding of at least one of the three theoretical frameworks (Z, T, or H)
- Access to the platform's source code repository at a tagged version

---

## Part B: Assessment Protocol

### B1. Platform Preparation

1. **Clone** the platform source code at a specific tagged release or commit hash
2. **Document** the exact version (release name, build number, commit hash, date)
3. **Set up** a local development instance if runtime testing (R-type evidence) is planned
4. **Locate** the platform's API documentation and developer reference

### B2. Evidence Types and Hierarchy

Each score must be justified by specific evidence. Four evidence categories exist, in decreasing strength:

| Type | Code | Description | Example |
|------|------|-------------|---------|
| **Source Code** | **S** | Direct inspection of platform source code | Class names, method signatures, file paths, import relationships |
| **API Documentation** | **A** | Published API endpoints, web service definitions | REST endpoint specifications, SDK function signatures |
| **Runtime** | **R** | Observed behavior from a running instance | API call responses, event firing, measured latency |
| **Documentation** | **D** | Official docs describing capability | Developer guides, release notes, architecture overviews |

**Evidence requirements by score:**

| Score | Minimum Evidence |
|-------|-----------------|
| 0 (Absent) | S-type confirming absence (searched relevant directories, no code found) |
| 1 (Nascent) | At least one S-type or A-type item |
| 2 (Partial) | At least one S-type AND one A-type item |
| 3 (Substantial) | At least two S-type AND one A-type item |
| 4 (Ready) | At least two S-type AND one A-type AND one R-type or D-type item |

### B3. Step-by-Step Assessment Procedure

For each of the 32 sub-dimensions:

1. **Read** the sub-dimension definition and framework grounding
2. **Collect** evidence using the evidence checklist (search relevant source directories, API definitions, documentation)
3. **Score** by matching the collected evidence against the rubric criteria (0-4)
4. **Record** the score, evidence type codes, and evidence description in the scoring worksheet
5. **Flag** any uncertainty or ambiguity for discussion (if multi-rater)

### B4. Time Estimate

| Platform Familiarity | Estimated Duration |
|----------------------|-------------------|
| Expert (knows codebase) | 8-12 hours |
| Intermediate (knows LMS concepts) | 16-24 hours |
| Novice (first time with this platform) | 30-40 hours |

---

## Part C: Rubric Tables

### Ordinal Scale Definition

| Score | Label | General Definition |
|-------|-------|--------------------|
| **0** | **Absent** | No capability or infrastructure exists for this sub-dimension |
| **1** | **Nascent** | Primitive building blocks exist that could be repurposed but are not designed for this purpose |
| **2** | **Partial** | Dedicated functionality exists but is incomplete, not externally accessible, or batch-only |
| **3** | **Substantial** | Functional and accessible capability with specific, documented gaps |
| **4** | **Ready** | Production-ready: full functionality, API accessible, documented, architecturally appropriate |

---

### LEVEL 1: EVENT SENSING (5 sub-dimensions)

#### 1.1 Event Coverage and Classification
**Definition:** The breadth and pedagogical classification of events the platform emits about learning activities.
**Framework Grounding:** Z (observability of SRL phases) + T (perception breadth) + H (C1 context understanding)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No structured event system exists; actions are not logged as discrete events | S: No event class hierarchy or logging framework found |
| 1 | Basic logging exists (e.g., access logs, error logs) but events are not classified by educational significance | S: Log tables/files exist; no pedagogical metadata |
| 2 | Structured event system with typed events covering major activities (submissions, views, grades) but no educational classification metadata | S: Event classes exist; A: Events queryable; gap in edulevel or pedagogical tagging |
| 3 | Comprehensive event system covering 80%+ of learning activities, with educational classification (e.g., student vs teacher, CRUD type) and context metadata | S: 100+ event classes with edulevel/classification; A: Events accessible via API or observer pattern |
| 4 | All learning-relevant activities emit events with educational classification, context hierarchy, user identification, and custom extensibility | S: Event base class with edulevel, context, CRUD, target fields; extensible via plugins; A: Full observer subscription mechanism |

#### 1.2 Observer/Subscription Mechanism
**Definition:** The ability for external consumers (including agents) to subscribe to and receive events.
**Framework Grounding:** T (reactive agent triggers) + H (C1 real-time context awareness)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No mechanism for any system to subscribe to events | S: No observer pattern, webhook, or event bus code |
| 1 | Events are stored in a database table that can be queried retrospectively | S: Log store table exists; events persisted; no real-time subscription |
| 2 | Internal observer/hook pattern allows platform plugins to subscribe to events synchronously | S: Observer registration mechanism (e.g., db/events.php); callback dispatch code |
| 3 | Internal observers plus at least one mechanism for external event delivery (log store plugins, polling API, or webhook) | S: Internal observers + log store plugin architecture or change-detection API; A: Polling endpoint documented |
| 4 | Full subscription management: internal observers + external streaming (WebSocket, SSE, message bus) with filtering and consumer management | S+A: Streaming endpoint; consumer registration; event type filtering; R: Measured sub-minute latency |

#### 1.3 SRL Phase Observability
**Definition:** Whether events capture sufficient signals to infer student self-regulated learning phases (Forethought, Performance, Self-Reflection).
**Framework Grounding:** Z (all three SRL phases) + H (C4 progress monitoring signals)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | Events capture only system-level actions (login/logout) with no learning behavior signals | S: Only authentication/admin events |
| 1 | Events capture content access (views) — sufficient for basic Performance phase observation | S: View/access events exist |
| 2 | Events cover Performance (submissions, attempts, content access) and partial Reflection (grade viewing, feedback viewing) | S: Submission, attempt, grade-view events; gap: Forethought events absent |
| 3 | Events cover Performance (rich), Reflection (grade/feedback/re-attempt), and proxy Forethought indicators (resource browsing sequences, planning-tool access) | S: Events for all three phases; documented gap in direct Forethought signals |
| 4 | Events explicitly support all three SRL phases including direct Forethought signals (goal-setting, study planning) and metacognitive indicators | S: Goal/plan events; struggle/confusion proxies; self-assessment events |

#### 1.4 Real-Time External Access
**Definition:** The ability for systems outside the platform process to receive events in real-time or near-real-time.
**Framework Grounding:** T (perception for external agents) + H (C1 deployed agent context)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No external access to event data; events are PHP/Python-internal only | S: Events dispatched within request cycle only; no external endpoint |
| 1 | Events persisted to a queryable log store; external systems can poll with multi-minute latency | S: Log store table; A: No real-time endpoint; polling viable |
| 2 | Polling API exists with structured response (e.g., "changes since timestamp") | S: Polling endpoint code; A: Documented endpoint; latency = cron frequency |
| 3 | Near-real-time delivery via log store plugin forwarding to external queue, or webhook mechanism | S: Forwarding plugin or webhook code; A: Configuration docs; R: Latency <60s |
| 4 | Sub-second streaming via WebSocket, SSE, or native message bus with external consumer support | S: Streaming server code; A: Consumer API docs; R: Measured <1s latency |

#### 1.5 Event Enrichment and Context
**Definition:** Whether events carry sufficient resolved data for agent decision-making, or only contain raw identifiers requiring additional lookups.
**Framework Grounding:** H (educationally meaningful context) + Z (self-observation data richness)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | Events carry no contextual data beyond a log message string | S: Flat log entries without structured fields |
| 1 | Events carry entity IDs (user ID, course ID, object ID) but no resolved data | S: Event fields include IDs; no grade values, completion states, or contextual information |
| 2 | Events carry IDs plus basic context (course context, component name, action type, timestamp) | S: Structured event with context hierarchy; A: Event payload documented |
| 3 | Events carry IDs, context, and selected resolved data (e.g., completion state in completion events, grade value in grade events) via the `other` field or equivalent | S: Event-specific payload data; some events include resolved values |
| 4 | Events carry full context including resolved entity data, prior state, educational metadata, and support custom enrichment via plugins | S: Rich payloads; plugin extensibility for event data; A: Enrichment API documented |

---

### LEVEL 2: STUDENT STATE (6 sub-dimensions)

#### 2.1 Raw Data Availability
**Definition:** Whether the platform stores the fundamental data needed to model learner state (grades, completion, activity logs, competencies).
**Framework Grounding:** Z (self-judgment data) + T (long-term memory stores)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No persistent learner data beyond authentication records | S: No grade, completion, or activity tables |
| 1 | Basic grade storage (final grades only) and login records | S: Grade table exists; no completion tracking; no activity logs |
| 2 | Grades, activity completion, and event logs stored; competency/learning-path data absent | S: Grade + completion + log tables; gap in competency or learning standards |
| 3 | Comprehensive data: grades with history, completion per activity, event logs, competency tracking, and basic prediction data | S: Grade history table; completion tracking; competency framework; analytics predictions |
| 4 | All of the above plus temporal engagement metrics (time-on-task, session analysis), learning-path data, and self-reported learner data | S: Time tracking; session tables; learner profile data; learning standards integration |

#### 2.2 API Queryability
**Definition:** Whether stored learner data is accessible to external systems via documented APIs.
**Framework Grounding:** T (memory access for agents) + H (C4 progress query capability)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No API for querying learner data; direct database access required | S: No web service functions for grades/completion |
| 1 | A few basic API endpoints exist (e.g., course listing, user profile) but not learner-specific state | A: API docs show basic endpoints; gap in grade/completion APIs |
| 2 | APIs exist for major data types (grades, completion) but with gaps (no prediction API, no grade history) | S: Web service functions for grades and completion; A: Documented; gap in predictions or history |
| 3 | Comprehensive APIs covering grades, completion, competencies, and enrollment with token-based auth; some gaps remain (predictions, temporal metrics) | S: 100+ web service functions; A: Full API documentation; gap list documented |
| 4 | Full API coverage including predictions, grade history, temporal metrics, and learner model summary endpoint | S+A: All learner data types queryable; R: API calls return expected data |

#### 2.3 Predictive Analytics
**Definition:** Whether the platform can generate predictions about learner outcomes (dropout risk, completion likelihood, performance trajectory).
**Framework Grounding:** Z (identifying SRL breakdowns) + H (C4 at-risk detection)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No analytics or prediction capability | S: No analytics framework code |
| 1 | Basic reporting (counts, averages) but no predictive models | S: Report generation code; no ML pipeline |
| 2 | Prediction framework exists with at least one trained model (e.g., dropout prediction) but batch-only, cron-dependent | S: ML pipeline code; prediction targets; batch processing; no real-time predictions |
| 3 | Multiple prediction targets (dropout, completion, engagement) with configurable time-splitting; predictions accessible internally but not via API | S: 3+ prediction targets; time-splitting strategies; CoI or similar indicators; gap: no prediction API |
| 4 | Real-time or on-demand predictions accessible via API; multiple models; configurable indicators; feedback loop (prediction usefulness tracking) | S+A: Prediction API endpoint; R: On-demand prediction returns results; feedback mechanism exists |

#### 2.4 Unified Learner Model
**Definition:** Whether the platform provides a single, coherent query point that aggregates learner state across all data sources (grades, completion, analytics, competencies, engagement).
**Framework Grounding:** T (coherent agent memory) + H (C1+C4 holistic learner understanding)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No aggregation of learner data; each subsystem stores data independently with no cross-referencing | S: Separate tables/APIs with no aggregation layer |
| 1 | Basic user profile exists but does not include learning state (grades, completion, predictions) | S: User profile API returns demographics only |
| 2 | Multiple APIs can be called separately to assemble a partial learner picture (e.g., grades API + completion API) | A: Separate endpoints exist; no single aggregation call; agent must synthesize |
| 3 | A near-unified view exists (e.g., course-level dashboard data combining grades, completion, and predictions) but not exposed as a single API for agent consumption | S: Dashboard/report code aggregates data; not API-accessible |
| 4 | Single API endpoint returns a holistic learner profile per student per course: grades, completion, predictions, competencies, engagement metrics, and historical trajectory | S+A: Learner model service endpoint; R: Returns aggregated JSON profile |

#### 2.5 Agent Memory Support
**Definition:** Whether agents can store and retrieve their own state (working memory, conversation history, intervention records) through platform-provided mechanisms.
**Framework Grounding:** T (short-term/working memory) + H (C2 adaptive interaction state)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No mechanism for agents to persist state; each interaction is fully stateless | S: AI/agent subsystem has no state storage; each request independent |
| 1 | Generic key-value cache exists that could be repurposed for agent state, but not designed for it | S: Cache API exists (e.g., Moodle cache, Redis); no agent-specific schema |
| 2 | Agent actions are logged (audit trail) but not queryable as agent memory; no conversation history | S: Action log/register table exists; A: Log query possible; no structured memory API |
| 3 | Basic agent state storage exists: per-user or per-session state that agents can read/write; no TTL or versioning | S: State store mechanism; A: Read/write API; gap in TTL, versioning, or per-agent isolation |
| 4 | Full agent memory: per-agent + per-student state with TTL, versioning, conversation history, and intervention tracking | S+A: Dedicated agent memory tables; CRUD API; R: State persists across sessions |

#### 2.6 Real-Time State Queries
**Definition:** Whether learner state is queryable with low latency for real-time agent decision-making, versus batch-only or stale data.
**Framework Grounding:** T (memory retrieval latency) + H (C1 current context)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | Learner data only accessible via direct database queries or batch exports | S: No API; data in DB tables only |
| 1 | APIs exist but return potentially stale data (e.g., last cron run, cached values) | A: API returns data; S: Cron-dependent freshness |
| 2 | Most current state queryable in real-time (grades, completion); some data stale (predictions, analytics) | A: Grade/completion APIs return current data; prediction data is batch-refreshed |
| 3 | All major state types queryable with sub-minute freshness; event-driven cache invalidation | S: Cache invalidation on state change; A: APIs documented with freshness guarantees |
| 4 | All state queryable in real-time with push notifications on state changes (e.g., grade updated event triggers agent re-evaluation) | S+A: State-change webhooks or subscriptions; R: Measured freshness <10s |

---

### LEVEL 3: AGENT REASONING (6 sub-dimensions)

#### 3.1 LLM Infrastructure
**Definition:** Whether the platform provides infrastructure for connecting to and managing LLM providers (API keys, rate limiting, model selection, audit).
**Framework Grounding:** T (planning tool access) + H (C3 explanation generation capability)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No LLM or AI provider integration capability | S: No AI subsystem code |
| 1 | Third-party plugin can connect to one LLM provider; no core support | S: Plugin code for one provider; no core AI framework |
| 2 | Core AI subsystem with at least one provider; basic text generation; no rate limiting or audit | S: AI manager class; provider interface; gap in rate limiting or audit |
| 3 | Multiple LLM providers with rate limiting, audit logging, and configurable model selection; content-generation actions | S: 3+ providers; rate limiter; audit table; A: Provider configuration docs |
| 4 | Full AI infrastructure: multiple providers, rate limiting, audit, policy management, failover, cost tracking, and extensible action types | S: Provider failover; policy controls; A: Full admin configuration; R: Actions execute correctly |

#### 3.2 Agent Reasoning Capability
**Definition:** Whether the platform supports autonomous multi-step reasoning: goal decomposition, strategy selection, outcome simulation, and decision-making loops.
**Framework Grounding:** T (goal decomposition, strategy selection) + H (C2+C5 adaptive and metacognitive decision-making)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No reasoning support; AI is request-response only (single prompt, single output) | S: AI actions are stateless, one-shot; no agent loop |
| 1 | AI actions can be chained manually (output of one becomes input of next) but no automated reasoning loop | S: Action API allows sequential calls; no orchestration |
| 2 | Basic tool-use pattern: AI can call platform functions as tools (e.g., query grades before generating response) | S: Tool-use or function-calling integration; limited to predefined tools |
| 3 | Agent loop exists: observe state -> reason -> plan -> act cycle with configurable strategies; limited pedagogical guardrails | S: Agent loop/state machine code; strategy selection; gap in pedagogical constraints |
| 4 | Full agent reasoning: observe-reason-plan-act loop with pedagogical guardrails, outcome simulation, configurable intervention thresholds, and human-in-the-loop overrides | S+A: Agent framework with guardrails; R: Agent makes contextually appropriate decisions |

#### 3.3 AI-Analytics Integration
**Definition:** Whether the AI/LLM subsystem and the analytics/prediction subsystem are architecturally connected, allowing AI to consume predictions and analytics to trigger AI actions.
**Framework Grounding:** Z (connecting state observation to intervention) + H (C4 informing C2 adaptive learning)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | AI and analytics subsystems have zero cross-imports or shared interfaces; completely isolated | S: grep for cross-imports returns 0 results |
| 1 | Both subsystems exist independently; a plugin could theoretically bridge them via database queries | S: Both subsystems present; no integration code; shared DB accessible |
| 2 | Partial bridge: analytics predictions can be queried by AI actions through a manual intermediary (e.g., custom web service) | S: Bridge plugin or custom service code exists; not core architecture |
| 3 | Core integration: AI actions receive learner analytics data in their context; analytics can trigger AI actions via events or hooks | S: Analytics data passed to AI action context; event-based triggering |
| 4 | Bidirectional integration: AI consumes predictions and learner model; AI intervention outcomes feed back into analytics for model refinement | S+A: Bidirectional data flow; outcome tracking feeds analytics; R: Closed feedback loop observed |

#### 3.4 Scaffolding Support
**Definition:** Whether the platform supports graduated scaffolding — progressive support from hints to explanations to full solutions, respecting learner autonomy.
**Framework Grounding:** Z (graduated Intervention Delivery without dependency) + H (C3 scaffolded explanations)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No scaffolding capability; AI generates one-shot responses with no progression model | S: No scaffolding state or progression tracking |
| 1 | AI can generate explanations of content but with no awareness of prior interactions or progression | S: Explain/summarize action exists; no history |
| 2 | AI generates responses with basic context (current activity, user ID) but no scaffolding progression tracking | S: Context passed to AI; no hint/explanation sequence management |
| 3 | Scaffolding progression tracked per student per activity (hint -> clue -> explanation -> solution); AI aware of progression state | S: Progression state storage; escalation logic; gap in de-escalation or autonomy support |
| 4 | Full graduated scaffolding with de-escalation (pulling back support as mastery increases), learner autonomy preservation, and configurable scaffolding strategies | S+A: Bidirectional scaffolding; autonomy rules; R: Scaffolding adapts to demonstrated competence |

#### 3.5 Adaptive Learning
**Definition:** Whether the platform enables AI to modify the learning experience based on learner state (difficulty adjustment, content reordering, path personalization).
**Framework Grounding:** Z (adjusting to SRL phase) + H (C2 adaptive learning)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No mechanism for programmatic content or activity modification | S: No API for modifying course content or parameters |
| 1 | Static conditional access rules exist (teacher-configured) but not modifiable by agents at runtime | S: Availability conditions in code; teacher-only configuration |
| 2 | Some activity parameters modifiable via API (e.g., completion status override) but not learning-path parameters (difficulty, sequencing) | A: Coarse-grained update APIs exist; gap in fine-grained activity parameters |
| 3 | APIs exist for modifying activity availability, sequencing, and selected parameters; agent can adjust learning path for individual students | S+A: Per-student availability modification; activity parameter APIs |
| 4 | Full adaptive learning: agent can modify difficulty, reorder content, create personalized paths, and adjust assessment parameters per student in real-time | S+A: Fine-grained APIs; R: Agent-driven adaptation observed; per-student state maintained |

#### 3.6 Learner-Aware AI
**Definition:** Whether AI/LLM actions have access to learner model data (grades, completion, predictions, competency levels) when generating responses.
**Framework Grounding:** Z (context for intervention timing) + H (C1 in AI reasoning context)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | AI actions receive no learner data; only system context (e.g., text to summarize) | S: AI action context contains content only; no user state |
| 1 | AI actions receive user ID and course ID but no learner state data | S: User/course IDs in action context; no grade/completion/prediction data |
| 2 | AI actions receive basic context (current activity, user role) plus course-level information | S: Activity context in AI action; gap in personal learner state |
| 3 | AI actions receive learner model data: grades, completion percentage, prediction scores, and competency levels alongside the content context | S: Learner state injected into AI action context; A: Documented enrichment |
| 4 | Full learner awareness: AI receives comprehensive learner profile (grades, trajectory, predictions, competencies, interaction history, SRL phase indicators) with privacy controls | S+A: Full profile in context; privacy/consent filters; R: AI references learner data in output |

---

### LEVEL 4: ORCHESTRATION (7 sub-dimensions)

#### 4.1 Agent Registration and Identity
**Definition:** Whether the platform maintains a registry of agents with distinct identities, capabilities, roles, and permissions.
**Framework Grounding:** T (multi-agent collaboration — agent discovery)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No concept of distinct agent entities; AI is a monolithic service | S: No agent registry, agent table, or agent identity mechanism |
| 1 | AI providers are registered (LLM backends) but not individual agents with distinct roles | S: Provider registry exists; no agent identity layer |
| 2 | Agents can be deployed as separate plugins with distinct names but share a single identity model | S: Plugin-based agents; no capability declaration or role specialization |
| 3 | Agent registry with identity, capability declaration, target context, and priority levels; no dynamic registration | S: Agent registry tables; capability schema; A: Registration API |
| 4 | Full agent registry: dynamic registration, capability negotiation, role-based permissions, health monitoring, and versioning | S+A: Dynamic registration API; health checks; R: Agents discoverable at runtime |

#### 4.2 Shared State Management
**Definition:** Whether multiple agents can read and write to a shared learner state model with consistency guarantees.
**Framework Grounding:** T (shared memory) + Z (coordinated SRL phase awareness)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No shared state mechanism; each agent (or AI action) operates in isolation | S: No shared state store; stateless processing |
| 1 | Generic shared storage exists (cache, database) that could be repurposed, but no agent-aware schema or concurrency control | S: Cache/DB available; no agent-specific state management |
| 2 | Agents can read shared platform data (grades, completion) but cannot write shared agent state | S+A: Read APIs exist; no agent write mechanism for shared state |
| 3 | Shared agent state store with read/write access and basic locking; no optimistic concurrency or versioning | S: Shared state tables; A: Read/write API; gap in concurrency control |
| 4 | Shared state store with optimistic concurrency control, versioning, per-student partitioning, and conflict detection | S+A: Versioned state store; concurrency control; R: Concurrent agent writes handled correctly |

#### 4.3 Coordination Protocols
**Definition:** Whether the platform provides mechanisms for agents to coordinate their actions (turn-taking, priority negotiation, handoff).
**Framework Grounding:** T (turn-taking, priority) + H (complementary agent specialization)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No coordination mechanism; agents act independently and may conflict | S: No coordination code |
| 1 | Basic priority ordering exists (e.g., plugin sort order) that indirectly affects agent execution order | S: Priority/sort mechanism; not agent-specific |
| 2 | Agents can declare non-overlapping scopes (e.g., different course modules) reducing conflict potential | S: Scope declaration; agent assignment to contexts |
| 3 | Coordination protocol: agents can signal intent before acting, check for conflicts, and defer to higher-priority agents | S: Intent signaling; conflict check API; A: Protocol documented |
| 4 | Full coordination: turn-taking, priority negotiation, SRL-phase-based handoff (Forethought agent -> Performance agent -> Reflection agent), and deadlock prevention | S+A: Handoff protocol; deadlock prevention; R: Multi-agent scenario executes correctly |

#### 4.4 Conflict Resolution
**Definition:** Whether the platform detects and resolves conflicts when multiple agents propose contradictory actions for the same student.
**Framework Grounding:** T (conflict handling) + Z (pedagogical coherence across SRL phases)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No conflict detection; last-write-wins or undefined behavior | S: No conflict detection code |
| 1 | Audit logging would allow post-hoc conflict identification, but no real-time detection | S: Audit trail; no real-time conflict check |
| 2 | Basic conflict detection: system can identify when two agents target the same student simultaneously | S: Concurrent action detection logic |
| 3 | Conflict detection plus resolution strategies (priority-based, role-based, or human-escalation) | S: Resolution strategy code; A: Configuration for strategy selection |
| 4 | Comprehensive conflict resolution with pedagogical coherence rules (e.g., do not simultaneously encourage and discourage an activity), automatic resolution, and human override | S+A: Pedagogical rules; automatic resolution; R: Conflicting actions resolved correctly |

#### 4.5 Inter-Agent Communication
**Definition:** Whether agents can exchange messages, share observations, or request assistance from other agents.
**Framework Grounding:** T (agent-to-agent message passing)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No inter-agent communication channel | S: No message bus, pub/sub, or agent messaging code |
| 1 | Agents can observe each other's actions indirectly via shared database/log tables | S: Action log queryable; agents can see what others did |
| 2 | Broadcast mechanism exists (e.g., event system) that agents can use to publish observations | S: Agents can fire events; other agents can observe |
| 3 | Point-to-point and broadcast messaging between agents with typed message schemas | S: Agent message types; routing; A: Messaging API documented |
| 4 | Full communication: request/response, publish/subscribe, broadcast, with message history and delivery guarantees | S+A: Full messaging system; delivery guarantees; R: Inter-agent messages delivered correctly |

#### 4.6 Agent Lifecycle Management
**Definition:** Whether the platform supports deploying, configuring, monitoring, pausing, and removing agents per course or cohort.
**Framework Grounding:** T (agent deployment and monitoring)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No agent lifecycle management; agents are static code deployments | S: No agent admin interface or management API |
| 1 | Agents are deployed as plugins with enable/disable at the site level | S: Plugin enable/disable; no per-course granularity |
| 2 | Per-course or per-activity agent configuration possible (e.g., enable/disable writing coach for a specific course) | S: Course-level agent settings; A: Configuration API |
| 3 | Full lifecycle: deploy, configure, monitor (activity logs), pause, and remove agents per context with admin dashboard | S: Admin interface; lifecycle API; monitoring dashboard; A: Documented |
| 4 | Advanced lifecycle: A/B testing of agents, gradual rollout, performance monitoring, automatic scaling, and version management | S+A: A/B testing; versioning; auto-scaling; R: Lifecycle operations observed |

#### 4.7 Infrastructure Building Blocks
**Definition:** Whether the platform provides reusable primitives (task queues, caching, message systems) that could support orchestration even if not designed for it.
**Framework Grounding:** (Platform engineering — foundational enabler)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No relevant infrastructure beyond basic request-response processing | S: No queue, cache, or async processing |
| 1 | Basic cron/task scheduler exists for deferred processing | S: Scheduled task system; cron-based execution |
| 2 | Task queue + cache system suitable for agent state and async operations | S: Ad-hoc tasks; cache API; suitable for repurposing |
| 3 | Task queue + cache + capability/permission system + hook architecture for extensibility | S: Capability system; hook/event architecture; A: Extension points documented |
| 4 | Full infrastructure: task queue, distributed cache, message bus, capability system, hook architecture, and health monitoring | S+A: All primitives present; R: Infrastructure handles agent-scale workloads |

---

### LEVEL 5: INTERVENTION DELIVERY (8 sub-dimensions)

#### 5.1 Basic Message Delivery
**Definition:** Whether agents can send messages or notifications to individual students through the platform.
**Framework Grounding:** Z (delivering SRL prompts) + H (C5 metacognitive prompts)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No programmatic messaging capability | S: No messaging API |
| 1 | Email-only notification system; no in-platform messaging | S: Email sending code; no in-app messages |
| 2 | In-platform messaging API exists but limited to plain text; no rich content | A: Messaging endpoint; S: Message creation code; gap in formatting |
| 3 | Rich messaging with HTML/structured content, notification preferences, and multiple channels (in-app, email, mobile push) | S: Multiple output plugins; A: Messaging API documented; message formatting supported |
| 4 | Full messaging: rich content, multiple channels, delivery confirmation, read tracking, and agent-identified sender | S+A: All channels; delivery tracking; agent identity in messages; R: Messages delivered and tracked |

#### 5.2 AI Content Generation for Interventions
**Definition:** Whether the platform can generate intervention content (explanations, summaries, feedback, prompts) via AI/LLM integration.
**Framework Grounding:** H (C3 scaffolded explanations) + T (action execution)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No AI content generation capability | S: No AI/LLM integration |
| 1 | Basic text generation via a single LLM provider (plugin-based, not core) | S: Plugin connecting to one LLM |
| 2 | Core AI subsystem with text generation and at least one other action type (summarize, explain, or image generation) | S: AI manager; 2+ action types; A: Action endpoints |
| 3 | Multiple action types across multiple providers with rate limiting, audit, and context-aware generation | S: 3+ action types; 3+ providers; rate limiter; audit trail; A: Documented |
| 4 | Full AI content generation: multiple actions, providers, failover, cost management, pedagogically-grounded prompt templates, and quality evaluation | S+A: All features; prompt template system; R: Generated content is contextually appropriate |

#### 5.3 Real-Time Delivery
**Definition:** Whether interventions can be delivered to students in real-time (sub-second to seconds), not dependent on page refresh or cron cycles.
**Framework Grounding:** Z (timely Intervention Delivery) + H (C2 responsive adaptation)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No push delivery mechanism; interventions only visible on next page load | S: No push/WebSocket/SSE code |
| 1 | Notifications appear on next page refresh or periodic polling (>30s intervals) | S: Polling-based notification code; AJAX refresh |
| 2 | Mobile push notifications exist; web client still polling-based | S: Mobile push integration; web polling; A: Push notification docs |
| 3 | Near-real-time for web and mobile via short polling (<10s) or long polling; most interventions delivered within 30 seconds | S: Short/long polling; A: Documented; R: Measured <30s delivery |
| 4 | Real-time push delivery via WebSocket or SSE for all clients; sub-second intervention delivery | S: WebSocket/SSE server; A: Real-time API; R: Measured <2s delivery |

#### 5.4 Interactive Interventions
**Definition:** Whether agent-delivered interventions can include interactive elements (buttons, scales, self-assessment prompts) that collect student responses.
**Framework Grounding:** Z (engaging self-reflection) + H (C5 interactive metacognitive prompts)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | Messages are text-only; no interactive elements | S: Plain text messages only |
| 1 | HTML messages can include links to external activities (e.g., link to a quiz) | S: HTML messaging; links possible |
| 2 | Messages can include basic action buttons (e.g., "Mark as helpful" / "Dismiss") | S: Action buttons in notifications; limited to pre-defined actions |
| 3 | Interactive interventions with configurable response options (Likert scales, multiple choice, free text) embedded in the notification/message | S: Interactive message types; response collection; A: Interaction API |
| 4 | Full interactive interventions: embedded self-assessment, mini-quizzes, reflection prompts, and response tracking with data fed back to agent reasoning | S+A: Embedded interactions; response data API; R: Student responses captured and available to agents |

#### 5.5 Content Injection
**Definition:** Whether agents can dynamically insert content into the student's learning flow (banners, tips, widgets within the course view) without requiring page navigation.
**Framework Grounding:** H (C2 adaptive content) + Z (in-context scaffolding)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No mechanism for dynamic content injection; all content is teacher-authored | S: No dynamic content insertion code |
| 1 | Block system exists allowing additional content panels, but blocks are teacher-configured, not agent-controlled | S: Block architecture; teacher-only configuration |
| 2 | Programmatic block/widget creation possible but requires plugin deployment, not runtime API calls | S: Block creation code; requires plugin; not per-student |
| 3 | API for inserting per-student dynamic content (banners, tips, recommendations) into course view | S+A: Content injection API; per-student targeting |
| 4 | Full content injection: per-student, per-context, real-time insertion and removal with priority ordering and display rules | S+A: Insertion/removal API; priority system; R: Dynamic content appears correctly per student |

#### 5.6 Activity and Content Modification
**Definition:** Whether agents can modify existing learning activities (quiz parameters, assignment settings, availability conditions) in response to learner state.
**Framework Grounding:** H (C2 adaptive learning) + Z (adjusting difficulty and scaffolding level)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No API for modifying activity parameters | S: No activity modification endpoints |
| 1 | Course-level update APIs exist (rename course, change settings) but not activity-parameter level | A: Course update API; no activity parameter APIs |
| 2 | Some activity parameters modifiable (e.g., completion override) but not learning-critical parameters (difficulty, time limits, grade boundaries) | A: Completion override API; gap in quiz/assignment parameter APIs |
| 3 | APIs for modifying most activity parameters including availability conditions, time limits, and attempt limits; per-student modification limited | S+A: Activity modification APIs; gap in per-student parameter overrides |
| 4 | Full modification: per-student parameter overrides (difficulty, content visibility, assessment criteria), with audit trail and teacher notification | S+A: Per-student overrides; audit; teacher alerts; R: Modifications applied and verified |

#### 5.7 Timing and Context-Aware Delivery
**Definition:** Whether the platform supports delivering interventions at pedagogically optimal moments (e.g., after 3 minutes of inactivity on a quiz, upon first login after a failed attempt).
**Framework Grounding:** Z (SRL phase-appropriate timing) + H (C2 responsive to learner context)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No timing control; interventions sent immediately when triggered by code | S: No scheduling or context-based triggering |
| 1 | Deferred execution via task scheduler (cron) with minute-level granularity | S: Scheduled/ad-hoc task system; cron-dependent timing |
| 2 | Event-triggered delivery: specific events (e.g., quiz submission) can trigger interventions via observer pattern | S: Observer-based triggering; immediate response to events |
| 3 | Event-triggered + time-delayed delivery: "send this message 5 minutes after quiz submission if no review started" | S: Conditional timing logic; delayed task scheduling with conditions |
| 4 | Full context-aware timing: complex trigger rules combining events, timing, learner state, and SRL phase with configurable delivery windows | S+A: Rule engine; complex trigger conditions; R: Interventions delivered at optimal moments |

#### 5.8 Intervention Effectiveness Tracking
**Definition:** Whether the platform tracks whether delivered interventions were received, engaged with, and effective (closing the feedback loop).
**Framework Grounding:** Z (feedback loop closure in SRL cycle) + H (C4 outcome monitoring)

| Score | Criteria | Required Evidence |
|-------|----------|-------------------|
| 0 | No tracking of intervention delivery or effectiveness | S: No tracking code |
| 1 | Basic audit logging of what was sent (action, content, recipient, timestamp) | S: Audit/action log table; gap in outcome tracking |
| 2 | Delivery confirmation (sent + viewed) tracked but no outcome correlation | S: Read receipt or view tracking; gap in effectiveness measurement |
| 3 | Delivery + engagement tracking (viewed, clicked, responded) plus basic outcome correlation (pre/post intervention performance) | S: Engagement metrics; outcome tracking; A: Tracking API |
| 4 | Full effectiveness tracking: delivery, engagement, learning outcome correlation, A/B comparison, and feedback to agent reasoning for strategy refinement | S+A: Full tracking pipeline; A/B support; R: Effectiveness data feeds back to agents |

---

## Part D: Scoring Worksheet

### D1. Score Entry Template

For each sub-dimension, record:

| Level | Sub-Dimension | Score (0-4) | Evidence Types | Evidence Summary | Confidence Notes |
|-------|--------------|-------------|----------------|------------------|-----------------|
| L1 | 1.1 Event Coverage | | | | |
| L1 | 1.2 Observer/Subscription | | | | |
| L1 | 1.3 SRL Phase Observability | | | | |
| L1 | 1.4 Real-Time External Access | | | | |
| L1 | 1.5 Event Enrichment | | | | |
| L2 | 2.1 Raw Data Availability | | | | |
| L2 | 2.2 API Queryability | | | | |
| L2 | 2.3 Predictive Analytics | | | | |
| L2 | 2.4 Unified Learner Model | | | | |
| L2 | 2.5 Agent Memory Support | | | | |
| L2 | 2.6 Real-Time State Queries | | | | |
| L3 | 3.1 LLM Infrastructure | | | | |
| L3 | 3.2 Agent Reasoning Capability | | | | |
| L3 | 3.3 AI-Analytics Integration | | | | |
| L3 | 3.4 Scaffolding Support | | | | |
| L3 | 3.5 Adaptive Learning | | | | |
| L3 | 3.6 Learner-Aware AI | | | | |
| L4 | 4.1 Agent Registration | | | | |
| L4 | 4.2 Shared State Management | | | | |
| L4 | 4.3 Coordination Protocols | | | | |
| L4 | 4.4 Conflict Resolution | | | | |
| L4 | 4.5 Inter-Agent Communication | | | | |
| L4 | 4.6 Agent Lifecycle Management | | | | |
| L4 | 4.7 Infrastructure Building Blocks | | | | |
| L5 | 5.1 Basic Message Delivery | | | | |
| L5 | 5.2 AI Content Generation | | | | |
| L5 | 5.3 Real-Time Delivery | | | | |
| L5 | 5.4 Interactive Interventions | | | | |
| L5 | 5.5 Content Injection | | | | |
| L5 | 5.6 Activity Modification | | | | |
| L5 | 5.7 Timing/Context-Aware Delivery | | | | |
| L5 | 5.8 Effectiveness Tracking | | | | |

### D2. Composite Score Calculation

**Step 1:** Compute arithmetic mean of sub-dimension scores per level.

**Step 2:** Apply minimum threshold rule: if any sub-dimension scores 0, the composite verdict cannot exceed "Partially Ready" (2.5 maximum).

**Step 3:** Map composite to readiness verdict:

| Composite Range | Readiness Verdict | Interpretation |
|-----------------|-------------------|----------------|
| 0.0 - 0.5 | **Not Ready** | Infrastructure absent; greenfield development required |
| 0.6 - 1.5 | **Foundation Only** | Building blocks exist; major development needed |
| 1.6 - 2.5 | **Partially Ready** | Significant capability with major gaps |
| 2.6 - 3.5 | **Substantially Ready** | Functional capability with targeted gaps |
| 3.6 - 4.0 | **Ready** | Production-viable for this STAIR level |

### D3. Sensitivity Analysis

Report composite scores under three weighting schemes:

**Scheme A — Equal Weights (default):**
All sub-dimensions weighted 1.0. Composite = arithmetic mean.

**Scheme B — Theoretical Priority (convergence-weighted):**
Sub-dimensions grounded in all three frameworks (Z+T+H) weighted 1.5x; others weighted 1.0x.

*Level 1 priority sub-dimensions (Z+T+H):* 1.1 Event Coverage
*Level 2 priority sub-dimensions:* (none — all are Z+T or T+H)
*Level 3 priority sub-dimensions:* 3.6 Learner-Aware AI
*Level 4 priority sub-dimensions:* 4.2 Shared State Management
*Level 5 priority sub-dimensions:* 5.1 Basic Message Delivery

**Scheme C — Agent Priority (operational-weighted):**
Sub-dimensions most critical for a minimal agent to function weighted 1.5x.

*Level 1:* 1.2 Observer/Subscription (agent must receive events)
*Level 2:* 2.2 API Queryability (agent must query state)
*Level 3:* 3.2 Agent Reasoning Capability (core agent function)
*Level 4:* 4.3 Coordination Protocols (core orchestration function)
*Level 5:* 5.3 Real-Time Delivery (intervention must reach student)

**Report format:**

| Level | Scheme A (Equal) | Scheme B (Theory) | Scheme C (Agent) | Variance |
|-------|-----------------|-------------------|------------------|----------|
| L1 | | | | |
| L2 | | | | |
| L3 | | | | |
| L4 | | | | |
| L5 | | | | |

If any level shows >0.5 variance between schemes, discuss implications.

### D4. Overall Readiness Profile Summary

| Level | Composite Score | Verdict | Minimum Sub-Dim | Threshold Rule Applied? |
|-------|----------------|---------|-----------------|------------------------|
| L1 | | | | |
| L2 | | | | |
| L3 | | | | |
| L4 | | | | |
| L5 | | | | |

**Overall platform position:** [Describe which levels are achieved and where the primary cliff exists]

---

## Part E: Inter-Rater Reliability Protocol

### E1. Multi-Rater Assessment Procedure

1. **Minimum raters:** 2 independent assessors (3+ recommended)
2. **Assessor independence:** Raters must complete their assessments before comparing results
3. **Shared preparation:** All raters use the same platform version, source code clone, and assessment protocol
4. **Scoring:** Each rater completes the full scoring worksheet independently

### E2. Agreement Measurement

Calculate **Cohen's weighted kappa** (linear weights) for each sub-dimension across rater pairs.

**Interpretation thresholds** (Landis & Koch, 1977):

| Kappa | Agreement Level | Action |
|-------|----------------|--------|
| < 0.20 | Slight | Rubric needs major revision — criteria are ambiguous |
| 0.21 - 0.40 | Fair | Rubric needs revision — criteria need sharpening |
| 0.41 - 0.60 | Moderate | Acceptable for pilot; consider refining |
| 0.61 - 0.80 | Substantial | Good — rubric is reliable |
| 0.81 - 1.00 | Almost Perfect | Excellent — rubric is highly reliable |

**Target:** All sub-dimensions should achieve kappa >= 0.61 (substantial agreement).

### E3. Disagreement Resolution

For disagreements of >1 ordinal level:
1. Both raters present their evidence
2. Discuss which rubric criteria are met
3. If unresolved, a third rater (or domain expert) adjudicates
4. Document the disagreement and resolution rationale

### E4. Pragmatic Approach for Single-Author Studies

When multi-rater assessment is not feasible (e.g., MSc or early-stage PhD research):
1. Complete the full assessment using the instrument
2. Have 2-3 colleagues independently score a **subset** (e.g., all of Level 1 — 5 sub-dimensions) using the same rubrics
3. Report the subset inter-rater agreement as a measure of rubric quality
4. Acknowledge single-rater limitation in the paper's threats to validity
5. Frame the instrument as enabling future multi-rater replication

---

## Part F: Machine-Readable Schema

For cross-platform comparison datasets, scores should be exportable in CSV format:

```csv
platform,version,assessor_id,date,level,subdimension_id,subdimension_name,score,evidence_types,evidence_summary
Moodle,5.2dev+,assessor_1,2026-03-25,L1,1.1,Event Coverage and Classification,4,"S,A","228 core event classes with edulevel; observer pattern via db/events.php"
Moodle,5.2dev+,assessor_1,2026-03-25,L1,1.2,Observer/Subscription Mechanism,2,"S","Internal observers via db/events.php; no external streaming"
```

Or JSON schema:

```json
{
  "platform": "string",
  "version": "string",
  "assessor_id": "string",
  "assessment_date": "YYYY-MM-DD",
  "scores": [
    {
      "level": "L1-L5",
      "subdimension_id": "1.1-5.8",
      "subdimension_name": "string",
      "score": 0-4,
      "evidence_types": ["S", "A", "R", "D"],
      "evidence_summary": "string",
      "confidence_notes": "string (optional)"
    }
  ]
}
```

---

## Appendix: Moodle 5.x Re-Scored Evaluation

Using this instrument, the Moodle 5.x (5.2dev+ Build 20260320) evaluation is re-scored from the original percentage-based assessment:

### Level 1: Event Sensing

| Sub-Dimension | Score | Evidence | Justification |
|--------------|-------|----------|---------------|
| 1.1 Event Coverage | **4** (Ready) | S: 228 core event classes with `edulevel`, `crud`, `contextid`, `target`, `action` fields; A: Observer pattern via `db/events.php` | Full event taxonomy with educational classification; plugin-extensible |
| 1.2 Observer/Subscription | **2** (Partial) | S: `core\event\manager::dispatch()` with internal/external observer separation; gap: no WebSocket, webhook, or message bus | Internal observers are robust; external agents must deploy as plugins or poll log store |
| 1.3 SRL Phase Observability | **2** (Partial) | S: Performance phase well-covered (submissions, attempts, views); Reflection partial (grade_report_viewed, feedback_viewed); Forethought weak (no goal/plan events) | Strong Performance, weak Forethought coverage |
| 1.4 Real-Time External Access | **1** (Nascent) | S: Events persisted to `mdl_logstore_standard_log`; A: `core_course_get_updates_since` polling API; no real-time endpoint | Polling only; multi-minute latency |
| 1.5 Event Enrichment | **2** (Partial) | S: Events carry IDs, context hierarchy, edulevel, `other` array; gap: no resolved entity data (grade values, completion states) in most events | Good metadata; agents must do additional lookups |

**Composite: (4+2+2+1+2)/5 = 2.2 → Partially Ready**
*Minimum threshold: no sub-dimension is 0 → no cap applied*
*Previous: 72% → now 2.2/4.0 (55th percentile on the new scale)*

### Level 2: Student State

| Sub-Dimension | Score | Evidence | Justification |
|--------------|-------|----------|---------------|
| 2.1 Raw Data Availability | **3** (Substantial) | S: `grade_grades`, `grade_grades_history`, `course_modules_completion`, `logstore_standard_log`, `competency_usercomp`, `analytics_predictions` tables | Comprehensive data; gap in time-on-task metrics |
| 2.2 API Queryability | **3** (Substantial) | S: 402 web service functions; A: `core_grades_get_gradeitems`, `core_completion_get_activities_completion_status`, 166 competency functions | Extensive API; gap in predictions and grade history endpoints |
| 2.3 Predictive Analytics | **2** (Partial) | S: 8 prediction targets, 6 indicators, CoI framework, ML pipeline; gap: batch-only (cron), no prediction API endpoint | Full ML pipeline but batch-only |
| 2.4 Unified Learner Model | **0** (Absent) | S: Data scattered across 5+ subsystems; no aggregation service | Critical gap — no unified query point |
| 2.5 Agent Memory Support | **0** (Absent) | S: AI subsystem (`core_ai`) is fully stateless; `ai_action_register` is audit trail only | No working memory, no conversation state |
| 2.6 Real-Time State Queries | **2** (Partial) | A: Grade/completion APIs return current data; predictions are cron-refreshed | Current state queryable; analytics stale |

**Composite: (3+3+2+0+0+2)/6 = 1.67 → Partially Ready**
*Minimum threshold: two sub-dimensions are 0 → capped at "Partially Ready" (confirmed)*
*Previous: 58% → now 1.67/4.0 (42nd percentile)*

### Level 3: Agent Reasoning

| Sub-Dimension | Score | Evidence | Justification |
|--------------|-------|----------|---------------|
| 3.1 LLM Infrastructure | **3** (Substantial) | S: 6 providers (OpenAI, Azure, Bedrock, Gemini, DeepSeek, Ollama), 4 actions, rate limiter, audit; gap: no failover or cost tracking | Excellent foundation |
| 3.2 Agent Reasoning | **0** (Absent) | S: AI actions are request-response only; no agent loop, goal decomposition, or strategy selection | No reasoning capability |
| 3.3 AI-Analytics Integration | **0** (Absent) | S: Zero cross-imports between `ai/classes/` and `analytics/classes/` | Architecturally isolated |
| 3.4 Scaffolding Support | **1** (Nascent) | S: `explain_text` action exists; no progression tracking, no hint-to-solution escalation | One-shot explanations only |
| 3.5 Adaptive Learning | **0** (Absent) | S: No API for modifying quiz difficulty, content sequencing, or activity parameters per student | No adaptive capability |
| 3.6 Learner-Aware AI | **1** (Nascent) | S: AI actions receive `contextid`, `userid`; no grade, completion, or prediction data in AI context | IDs present; no learner state |

**Composite: (3+0+0+1+0+1)/6 = 0.83 → Foundation Only**
*Minimum threshold: three sub-dimensions are 0 → capped at "Partially Ready" (already below)*
*Previous: 25% → now 0.83/4.0 (21st percentile)*

### Level 4: Orchestration

| Sub-Dimension | Score | Evidence | Justification |
|--------------|-------|----------|---------------|
| 4.1 Agent Registration | **0** (Absent) | S: No agent entity concept; only provider registration | No agent identity model |
| 4.2 Shared State Management | **0** (Absent) | S: No shared agent state; cache system exists but not agent-aware | No shared state |
| 4.3 Coordination Protocols | **0** (Absent) | S: No coordination code | No coordination |
| 4.4 Conflict Resolution | **0** (Absent) | S: No conflict detection | No conflict handling |
| 4.5 Inter-Agent Communication | **0** (Absent) | S: No agent messaging | No communication |
| 4.6 Agent Lifecycle | **0** (Absent) | S: No agent management beyond plugin enable/disable | No lifecycle management |
| 4.7 Infrastructure Building Blocks | **2** (Partial) | S: Task queue (scheduled + ad-hoc), cache API, capability/permission system, hook architecture | Reusable primitives exist |

**Composite: (0+0+0+0+0+0+2)/7 = 0.29 → Not Ready**
*Minimum threshold: six sub-dimensions are 0 → capped at "Partially Ready" (already well below)*
*Previous: 8% → now 0.29/4.0 (7th percentile)*

### Level 5: Intervention Delivery

| Sub-Dimension | Score | Evidence | Justification |
|--------------|-------|----------|---------------|
| 5.1 Message Delivery | **3** (Substantial) | S: `core_message_send_instant_messages`; multiple channels (in-app, email, mobile push via output plugins) | Functional messaging; gap in agent sender identity |
| 5.2 AI Content Generation | **3** (Substantial) | S: 4 action types, 6 providers, rate limiting, audit; A: Web service endpoints documented | Strong content generation infrastructure |
| 5.3 Real-Time Delivery | **0** (Absent) | S: No WebSocket, SSE, or push for web clients; mobile relies on polling | No real-time push |
| 5.4 Interactive Interventions | **0** (Absent) | S: Messages are plain text/HTML; no embedded interactive elements | No interactivity |
| 5.5 Content Injection | **0** (Absent) | S: No dynamic per-student content injection API | No content injection |
| 5.6 Activity Modification | **1** (Nascent) | A: `core_completion_override_activity_completion_status` exists; no quiz/assignment parameter APIs | Very limited modification |
| 5.7 Timing/Context-Aware | **1** (Nascent) | S: Ad-hoc task system for deferred execution; cron-dependent (1-5 min latency) | Delayed execution only |
| 5.8 Effectiveness Tracking | **1** (Nascent) | S: `ai_action_register` logs AI actions; `analytics_predictions` has useful/not useful feedback; no intervention-outcome correlation | Audit trail exists; no effectiveness measurement |

**Composite: (3+3+0+0+0+1+1+1)/8 = 1.13 → Foundation Only**
*Minimum threshold: three sub-dimensions are 0 → capped at "Partially Ready" (already below)*
*Previous: 18% → now 1.13/4.0 (28th percentile)*

### Re-Scored Summary

| Level | Old Score (%) | New Composite (0-4) | Verdict | Min Sub-Dim |
|-------|--------------|--------------------|---------|----|
| L1: Event Sensing | 72% | **2.2** | Partially Ready | 1 (Real-Time Access) |
| L2: Student State | 58% | **1.67** | Partially Ready | 0 (Unified Model, Agent Memory) |
| L3: Agent Reasoning | 25% | **0.83** | Foundation Only | 0 (Reasoning, AI-Analytics, Adaptive) |
| L4: Orchestration | 8% | **0.29** | Not Ready | 0 (6 of 7 sub-dimensions) |
| L5: Intervention Delivery | 18% | **1.13** | Foundation Only | 0 (Real-Time, Interactive, Injection) |

**Key observations from re-scoring:**
- The ordinal scale eliminates spurious precision while preserving the relative ordering
- The minimum threshold rule correctly highlights that L2's composite (1.67) is constrained by two absent capabilities
- L5 > L4 is preserved and now clearly explained: L5 has messaging and AI infrastructure (scores of 3) boosting its average, while L4 is almost entirely absent. This reflects infrastructure readiness, not functional readiness — L5 cannot deliver effective interventions without L3-L4
- The cliff between L2 and L3 is even more stark on the ordinal scale (1.67 → 0.83)

---

*This instrument is provided as a supplementary contribution to the STAIR Framework paper. It is designed for reuse by the research community under CC BY 4.0.*
