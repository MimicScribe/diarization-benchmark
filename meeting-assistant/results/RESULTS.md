# Meeting Assistant Benchmark Results

Pipeline: Gemini 3 Flash (briefing) + Gemini 3.1 Flash Lite (action items) + Claude Sonnet (judge)

Run date: 2026-04-12 | 96 scenarios | 5 runs each

## Summary

| Metric | Value |
|--------|-------|
| Full-suite composite (96 scenarios × 5 runs, 2026-04-09 full-suite baseline) | 95.5% |
| Hallucination tag composite (re-measured 2026-04-12, 5 runs) | **97%** |
| Long-meetings tag composite (re-measured 2026-04-12, 5 runs) | **96%** (was 91%) |
| Avg latency (briefing call) | 1,760ms |
| p50 / p95 latency | 1,752ms / 2,122ms |
| Stability (cross-run consistency) | 88% avg |

The full 96-scenario suite was last run on 2026-04-09. Tag-specific re-runs on hallucination and long-meeting scenarios (the areas targeted by the 2026-04-12 prompt refinements) show improvement in the focused metrics. A full-suite re-measurement is pending.

## Hallucination (Targeted)

**6 scenarios** | **27/28 critical assertions pass on 5-run average** | **97% avg composite**

| Scenario | Score | Latency | Stability |
|----------|-------|---------|-----------|
| :white_check_mark: Prepared context bleeding into summary | 91% | 1757ms | 85% |
| :white_check_mark: Number/date mutation in dense financial discussion | 100% | 1598ms | 88% |
| :white_check_mark: Speaker name fabrication (anonymous participants) | 100% | 1655ms | 86% |
| :white_check_mark: Similar numbers across topics (confusion risk) | 100% | 1443ms | 92% |
| :white_check_mark: Partial transcript with sparse context | 100% | 1488ms | 92% |
| :white_check_mark: Competitor in context but not in transcript | **100%** | 1849ms | 88% |

The "competitor in context" scenario — previously at 78% — is now at 100% after the briefing system instruction was strengthened with a dedicated rule: commitments from any source (summary or recent transcript) are locked, and talking points must not generate "confirm/remind/verify/check" prompts about them.

### Concrete examples — what the system gets right

**Competitor context scenario** — prepared context includes *"Competitor intel: They evaluated Otter.ai last quarter and rejected it for privacy reasons"*. The transcript is a technical discussion about on-device processing and data residency that never names Otter.ai.

Output (5/5 runs, after the fix):
> *- Ask if on-device processing resolves their previous privacy concerns.*
> *- Ask how the CFO views the current technical progress.*
> *- Confirm the timeline for the CISO security review.*

The model picks up the privacy thread from prepared context as a topic to pursue without surfacing the specific competitor name unprompted. It focuses on actionable follow-ups that align with what was discussed.

**Dense financial scenario** — prepared context includes a board-meeting summary with CAC ($28K blended, $42K enterprise), LTV ($380K enterprise, $95K mid-market), NRR (112%), gross margin (78%), runway (22 months at $18M cash). All 14 financial metrics appear in output across 5 runs without mutation — no `$28K` → `$30K`, no `$380K` → `$400K`, no runway conversion.

### Known weakness — rapport notes leaking as technical pitches

One pattern that fails 1/5 runs on the dedicated test scenario: rapport-building notes in prepared context occasionally surface as technical talking points.

**Prepared context:**
> *"Internal note: Laura was previously at Snowflake — use this to build rapport."*

**Transcript:** Technical discussion about hybrid deployment, encryption, data residency — no mention of Snowflake.

**Failing output (1/5 runs):**
> *- Mention your Snowflake integration to see if it fits her roadmap.*

The named entity (`Snowflake`) is from prepared context as intended, but the framing turns a rapport cue into a technical pitch — conflating Laura's prior employer with the user's product integration. 20% failure rate on this specific scenario type; general "context bleeding" without named rapport notes is at 100%.

## Discovery Quality

**22 scenarios** | **108/113 assertions** | **96% avg composite**

Tests whether the assistant helps users understand the other party's situation — root causes, ideal outcomes, impact quantification, and unexplored requirements — rather than jumping to solutions or surface-level suggestions.

| Scenario Type | Count | Score | Avg Latency | Stability |
|---------------|-------|-------|-------------|-----------|
| Sales discovery (first calls, BANT gaps, workarounds) | 8 | 97% | 1575ms | 88% |
| Customer success (QBR expansion, workarounds, renewal) | 3 | 96% | 1577ms | 92% |
| User research (vague feedback, unused features, manual processes) | 3 | 100% | 1542ms | 89% |
| Interviews (technical depth, behavioral probing, collaboration) | 5 | 96% | 1776ms | 87% |
| Context density tiers (directive-only through rich context) | 3 | 92% | 1548ms | 89% |

**Failures:**

- [40%] [major] E1 interview — LLM judge inconsistently ruled discovery-deepening quality. Keyword assertions pass; judge is stricter on what counts as "probing deeper."
- [60%] [major] B1 compelling event — model asked about ideal outcomes instead of what's driving the evaluation. Keyword assertion too narrow for valid alternative phrasings.
- [0%] [major] Name from context not used — model given a name in prepared context but didn't apply it to the [Remote] speaker. Known limitation with minimal context.
- [0%] [major] G1 discovery-to-execution transition — model continues probing after BANT is fully addressed instead of suggesting next steps. Pre-existing gap; now measured with LLM judge.

### Interview Depth

**3 scenarios** | **19/20 assertions** | **98% avg composite**

Tests whether the assistant suggests follow-up questions that probe deeper into candidate responses — clarifying vague claims, testing technical depth, or digging into behavioral specifics.

| Scenario | Score | Key Behavior |
|----------|-------|-------------|
| :white_check_mark: System design — textbook answer, misses trade-offs | 100% | Probes exactly-once gap, data residency contradiction, suggests poison pill and backpressure |
| :white_check_mark: Behavioral — deflects on conflict, vague impact | 94% | Targets vague metrics ("ask for specific cycle time post-PIP") |
| :white_check_mark: Strong depth, dodges collaboration | 100% | Probes bypass-vs-delegation pattern, fires interpersonal on defensiveness |

### Context Density Tiers

Tests whether the minimal one-line template directive produces useful results without any additional context.

| Context Level | Composite | Notes |
|--------------|-----------|-------|
| Directive only (no name, no company) | 100% | Discovery-oriented talking points with zero user input |
| Directive + name and company | 78% | Model did not use the provided name |
| Directive + rich context (role, status, gaps) | 98% | Budget/authority gaps surfaced from context |
| Execution directive only | 100% | Correctly shifted to commitment tracking mode |

### Notable Outputs

Actual model outputs from discovery scenarios (unedited):

**Workaround detection** — customer mentions exporting to spreadsheets:
> - Ask what an ideal cross-product dashboard looks like.
> - Quantify the impact of **Marcus's** manual spreadsheet work.

**Workaround detection** — prospect's engineer maintains a fragile internal tool:
> - Ask what happens if replacement isn't live in **two months**.
> - Explore **ML pipeline** impact if Yusuf's time is freed.

**Interview depth** — candidate gives high-level caching answer without failure modes:
> - Ask how to handle **poison pill** tasks that crash consumers.
> - Ask about **backpressure** mechanisms when downstream services are slow.
> - Ask for a deep dive into **exactly-once** failure modes.

**Interview depth** — candidate dodges collaboration, does everything solo:
> - Ask how they handle **technical disagreements** during RFC reviews.
> - Ask how they **mentor** others to handle cross-team work.
> - Ask for an example of **delegating** a critical path task.

## Execution Quality (Goal & Commitment Tracking)

**28 scenarios** | **149/157 assertions** | **95% avg composite**

Tests whether the assistant tracks stated goals, surfaces unaddressed items at wrap-up, and drives toward commitments in late-stage meetings.

| Scenario Type | Count | Score | Avg Latency | Stability |
|---------------|-------|-------|-------------|-----------|
| Goal tracking (budget/timeline coverage, partial completion) | 3 | 100% | 1606ms | 89% |
| Wrap-up resurfacing (unaddressed goals at meeting end) | 5 | 99% | 1576ms | 89% |
| Complex domain-specific (sales, sprint, QBR, board, partner) | 6 | 90% | 2052ms | 84% |
| Execution-specific (closing, standup blockers, board decisions) | 3 | 100% | 1521ms | 87% |
| Standup & blocker ownership | 3 | 88% | 1780ms | 88% |
| Presentation coverage tracking | 4 | 99% | 1810ms | 88% |
| Discovery-to-execution transition | 2 | 89% | 1681ms | 85% |
| Long meetings with compacted summary | 1 | 100% | 1872ms | 87% |
| Context tier (execution directive) | 1 | 100% | 1548ms | 89% |

**Failures:**

- [20%] [major] Complex sprint planning — Elliot communication commitment surfaced in only 1/5 runs
- [40%] [major] Complex attribution dispute — missed surfacing the Friday deadline for the attribution model
- [40%] [major] Complex partner — model failed to surface the diagnostic tool next-step action
- [0%] [major] S1 standup — model consistently produces 4 bullets when 3 unowned blockers exist (legitimate content, exceeds 3-bullet limit)
- [0%] [major] G1 discovery-to-execution — model stays in discovery mode after BANT is fully addressed

### Standup & Blocker Ownership

**3 scenarios** | **17/20 assertions** | **88% avg composite**

Tests detection of unowned blockers and stalled handoffs in standup meetings.

| Scenario | Score | Key Behavior |
|----------|-------|-------------|
| :white_check_mark: Multiple blockers — some owned, some not | 88% | Catches all 3 unowned blockers (Adyen, infra pool, DevOps flag); exceeds bullet limit |
| :white_check_mark: Stalled handoffs with false-positive non-blockers | 100% | Flags auth keys and PR review; correctly ignores "relevance tuning" non-blocker |
| :large_orange_diamond: Everything on track — minimal expected | 75% | Generates filler talking points when nothing needs flagging |

### Customer Workaround Detection

**3 scenarios** | **23/23 assertions** | **100% avg composite**

Tests detection of workarounds and unexpressed needs in customer calls.

| Scenario | Score | Key Behavior |
|----------|-------|-------------|
| :white_check_mark: Spreadsheet workaround normalized as "just how we do it" | 100% | "Ask what Mateo's ideal automated workflow looks like" — connects ETL bottleneck to stalled ML model and European expansion |
| :white_check_mark: Frustrated customer masking pain behind "it's fine" | 100% | Surfaces parallel routing need, Janelle's spreadsheet, compliance risk. Fires interpersonal on "stopped asking" frustration |
| :white_check_mark: Happy customer with buried dependency risk | 100% | Catches Raj single-point-of-failure, suggests exploring native connectors |

### Presentation Coverage Tracking

**4 scenarios** | **28/28 assertions** | **99% avg composite**

Tests whether the assistant tracks prepared key points and surfaces uncovered ones.

| Scenario | Score | Key Behavior |
|----------|-------|-------------|
| :white_check_mark: Mid-talk — 2 of 4 points covered | 100% | Surfaces briefing latency and SSO (uncovered); does NOT re-surface ASR or diarization (covered) |
| :white_check_mark: Audience Q&A mid-presentation | 97% | Fires question detection, surfaces SOC 2 and encryption keys (uncovered) |
| :white_check_mark: All points covered — minimal expected | 100% | Produces only transitional bullets ("hand over to next speaker") |
| :white_check_mark: Dense financial metrics | 98% | Numbers perfectly preserved; surfaces runway and hiring (uncovered) |

### Wrap-up

**5 scenarios** | **24/24 assertions** | **99% avg composite**

| Scenario | Score | Key Behavior |
|----------|-------|-------------|
| :white_check_mark: Unaddressed budget (closing signals) | 100% | Budget surfaced as first bullet |
| :white_check_mark: Two goals unaddressed, meeting ending | 100% | CTO meeting and sign-off both surfaced |
| :white_check_mark: All goals met — no false resurfacing | 97% | No pricing reminder (confirmed); occasional transitional bullets |
| :white_check_mark: Conditional agreement (pending CISO) | 100% | Security review blocker surfaced |
| :white_check_mark: Vague verbal yes without specifics | 100% | Finance approval and timeline gaps surfaced |

## Interpersonal Awareness

**12 scenarios** | **42/48 assertions** | **94% avg composite**

| Scenario Type | Count | Score | Avg Latency | Stability |
|---------------|-------|-------|-------------|-----------|
| Tension detection with acoustic signals | 3 | 98% | 2023ms | 85% |
| Tension detection from text only | 1 | 90% | 1802ms | 78% |
| False positive suppression (enthusiasm, collaboration, technical speed) | 5 | 97% | 1662ms | 90% |
| Acoustic signal edge cases (disengagement, natural overlap) | 3 | 90% | 1826ms | 89% |

**Failures:**

- [0%] [major] Natural turn-boundary overlaps — model incorrectly flagged brief collaborative overlaps as interpersonal risk
- [67%] [major] Text-only disagreement — tension detected in 2/3 runs without acoustic signals (acceptable but inconsistent)

## Question Detection

**7 scenarios** | **17/19 assertions** | **89% avg composite**

| Scenario Type | Count | Score | Avg Latency |
|---------------|-------|-------|-------------|
| Unanswered remote question | 1 | 100% | 1417ms |
| Answered by user or other remote | 3 | 100% | 1348ms |
| User's own questions (must not surface) | 2 | 100% | 1434ms |
| Rhetorical question | 1 | 100% | 1719ms |
| Deflection without answering | 1 | 25% | 1468ms |

**Failures:**

- [0%] [critical] Deflection scenario — remote speaker says "can we circle back on that?" which is a non-answer, but the LLM judge ruled it answered in 3/3 runs

## Action Items

**4 scenarios** | **13/14 assertions** | **99% avg composite**

| Scenario Type | Count | Score | Avg Latency |
|---------------|-------|-------|-------------|
| Explicit commitments with due dates | 1 | 89% | 1653ms |
| Brainstorming rejection (no phantom items) | 1 | 100% | 1425ms |
| Mixed commitments and vague plans | 1 | 100% | 1580ms |
| No commitments (casual check-in) | 1 | 100% | 1330ms |

**Failures:**

- [67%] [critical] Due date grounding — one date resolved to the wrong day in 1/3 runs

## Incremental Action Items

**9 scenarios** | **23/27 assertions** | **94% avg composite**

Previous items preserved when transcript is unrelated, deadlines updated without duplication, cancelled items removed, aged-out items retained when supported by compacted summary.

## Long Meetings (90+ min)

**7 scenarios** | **29/32 assertions** | **96% avg composite**

| Scenario Type | Count | Score | Avg Latency | Stability |
|---------------|-------|-------|-------------|-----------|
| Multi-speaker all-hands (8 speakers) | 1 | 93% | 1688ms | 86% |
| Enterprise deal negotiation | 1 | 100% | 1706ms | 88% |
| Sprint planning continuation | 2 | 93% | 1608ms | 85% |
| Investor board update | 1 | 100% | 1692ms | 87% |

### Date preservation — "two weeks" stays "two weeks"

A concrete improvement: when the compacted summary contains commitments like *"Martin can have the CAC dashboard ready in two weeks"*, the briefing model now preserves the relative phrasing rather than converting to an absolute date.

**Earlier behavior:**
> *"Martin to deliver manual CAC dashboard by **April 23**"*

The model computed April 23 from "two weeks" and today's date (with the wrong arithmetic — April 12 + 14 = April 26, not April 23). More fundamentally, the summary is supposed to reflect what was said, not what the model infers.

**Current behavior (all 5 runs on the investor-board scenario):**
> *"Martin to deliver manual CAC dashboard in **two weeks**"*

Calendar resolution is handled separately by the action-items extraction model, which outputs both a resolved ISO `due` date and a verbatim `dueDescription` ("in two weeks") — giving users the calendar-ready date for scheduling alongside the original phrasing they can quote back to the speaker.

**Remaining weakness:** 2 real hallucinations in 35 runs, both in the enterprise-deal scenario where action-item due dates were occasionally still computed as absolute dates (a pre-existing issue in the action-items extraction, not the briefing summary).

### Compaction — the running summary that powers long-meeting briefings

Meetings past 15 minutes trigger a background compaction step that rolls older transcript (anything beyond the last 10 minutes) into a running summary. Over a 90-minute meeting this produces 12-19 compaction cycles, each inheriting the previous summary and merging in new content. The summary is then re-injected on every briefing call as `<MEETING_SUMMARY_SO_FAR>`, letting the briefing model reason about the whole meeting without seeing the full transcript.

Tested on 3 synthesized 80-minute marathon transcripts with 10-24 specific source numbers each:

| Metric | Baseline (3K cap, pre-redesign) | Current (12K cap, redesigned prompt) |
|--------|:-:|:-:|
| Number coverage (avg across 3 scenarios) | 40% | **83%** |
| Noun coverage (avg) | 60% | **72%** |
| Judge-flagged missing facts (total) | 35 | **13** |
| Relative date preservation | Mutates 4/5 runs | **5/5 runs preserve** |

**Compaction also improves downstream briefing quality** — perhaps counterintuitively, the briefing model produces better talking points from a compacted summary than from the full transcript (12 briefing samples per condition):

| Briefing metric | Full transcript in | **Compacted summary + recent window** |
|--------|:-:|:-:|
| Resurfacing avoidance | 33% | **50%** |
| No-hallucination pass rate | 83% | **100%** |
| Briefing latency | 3,071ms | **2,245ms (-27%)** |
| Input tokens | 11,726 | **4,996 (-57%)** |

The focused summary separates "settled" from "recent" content clearly. Full-transcript input overwhelms the model's forward-looking discipline and causes it to pull from anywhere in the meeting — including settled action items.

## Template Compliance

**2 scenarios** | **12/13 assertions** | **99% avg composite**

Output structure (question before bullets, interpersonal before divider, summary after divider), bold formatting, and bullet length limits all pass consistently.

## Known Weakness: Procedural Resurfacing at Meeting End

The most persistent failure mode across iterations: the briefing model occasionally suggests procedural "wrap-up" talking points that re-raise activities which just happened.

**Example** — sprint planning meeting that has visibly closed:

> *[You/Mic] Everyone good?*
> *[Remote] Good here.*
> *[Remote] Let's do it.*

**Failing output:**
> *- Ask if anyone has unresolved concerns before closing.*
> *- Confirm the meeting is adjourned.*
> *- Suggest a final review of the sprint board.*

All three bullets restate things the transcript just accomplished. The model defaults to "meeting-closing activities" as a safe output pattern even when those activities are visibly complete. This accounts for the 50% resurfacing rate observed in the compacted-briefing tests above.

**Where the model does well on specificity** — same scenario, different run, decisions still open:
> *- Ask how Alex's RFC should structure the caching invalidation strategy.*
> *- Confirm Nadia's written confirmation on promo code stacking tomorrow.*
> *- Ask Ravi about his plan for the Adyen webhook spike.*

Each bullet names specific people and topics from the source while adding a concrete angle rather than restating a commitment. Procedural-resurfacing is the fallback when the model cannot identify a net-new angle.

## Methodology

- **96 scenarios**, 5 runs each (480 total briefing API calls)
- **Deterministic assertions**: string matching, bullet counts, template structure, annotation leakage detection
- **LLM judge**: Claude Sonnet evaluates semantic quality (hallucination, grounding, forward-looking, discovery depth, interview depth, blocker ownership, workaround detection, presentation coverage, requirements surfacing)
- **Composite scoring**: Critical assertions weighted 3x, Major 2x, Minor 1x
- **Stability**: measured by bullet count variance and keyword Jaccard similarity across runs

See the [benchmark README](../README.md) for full assertion type documentation.
