# Meeting Assistant Benchmark Results

Pipeline: Gemini 3 Flash (briefing) + Gemini 3.1 Flash Lite (action items) + Claude Sonnet (judge)

Run date: 2026-04-18 (96-scenario suite) | 2026-04-22 (timezone subset, +7) | 103 scenarios total | 3–5 runs each

> **Partial re-measurement — 2026-04-18.** Discovery (22 scenarios) and execution (28 scenarios) were re-run at the current production config (temp 1.0, thinking=minimal) after a prompt-validation session where we A/B-tested three candidate prompt additions. Two candidates regressed quality and were dropped; one (softened `<PREVIOUS_BRIEFING>` instruction for the briefing call) was kept for its latency wins. Other categories (hallucination, interpersonal, action items, question detection, long meetings, template compliance) still reflect the 2026-04-12 numbers.

## Summary

| Metric | Value |
|--------|-------|
| Discovery composite (22 scenarios × 5 runs, 2026-04-18) | **96%** |
| Execution composite (28 scenarios × 5 runs, 2026-04-18) | **97%** |
| Hallucination tag composite (2026-04-12, 5 runs) | 97% |
| Long-meetings tag composite (2026-04-12, 5 runs) | 96% |
| Avg latency — discovery | **1,513ms** (was 1,666ms on 2026-04-17, 1,802ms on 2026-04-09) |
| Avg latency — execution | **1,520ms** (was 1,619ms on 2026-04-17, 1,802ms on 2026-04-09) |
| p95 latency — discovery / execution | 1,844ms / 1,984ms |
| p99 latency — discovery / execution | **1,998ms / 2,247ms** (was 2,728ms / 2,515ms on 2026-04-17) |
| Stability (cross-run consistency) | 82% avg |

Partial re-measurement covers the two largest subsets (50 of 96 scenarios). Latency improved substantially after softening the `<PREVIOUS_BRIEFING>` instruction to a shorter anti-flicker + recency-focused form — p99 dropped ~730ms on discovery and ~268ms on execution vs the stricter instruction from 2026-04-17. Stability is lower at production temperature (1.0) than the previously-hardcoded benchmark temperature (0.3) — an intentional tradeoff for useful talking-point variation on refresh.

## Prompt validation — what we tried and what stuck

This measurement cycle A/B-tested three candidate prompt additions. Principle: every instruction must justify its place — if it doesn't measurably improve quality, it's dropped to save tokens and latency.

| Candidate | Result | Decision |
|-----------|--------|----------|
| End-of-meeting summary "capture every substantive decision, commitment, number, named entity, deadline, unresolved question" (comprehensiveness) | template-summaries exact match 100% → 85% (-14.8pp), section recall 100% → 83.7%, usefulness 4.66 → 4.17, routing 0.849 → 0.759. summary-sections exact match 79.5% → 74.4%, routing 0.564 → 0.436. | **Dropped.** The instruction caused over-packing and misrouting. |
| End-of-meeting summary "separate sections with blank lines so RAG splits cleanly" (section formatting) | Measurement on 53 pre-change outputs: 100% already had blank-line separators without being told. Post-change: still 100%. | **Dropped.** Model already did it naturally. Instruction was dead weight. |
| Briefing `<PREVIOUS_BRIEFING>` softened from "preserve bullets verbatim, append new" to "emit summary if prior had one, focus on recent, replace superseded bullets" | Composite tied (-0.1pp both subsets). Latency p99 improved 730ms (discovery) / 268ms (execution). Shorter instruction → fewer tokens → faster. | **Kept.** No quality cost, latency win. |

## Hallucination (Targeted)

**6 scenarios** | **27/28 critical assertions pass on 5-run average** | **97% avg composite**

_(Last measured 2026-04-12 — numbers unchanged pending full-suite re-run.)_

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

**22 scenarios** | **102/113 assertions** | **96% avg composite** | **1,666ms avg latency**

Tests whether the assistant helps users understand the other party's situation — root causes, ideal outcomes, impact quantification, and unexplored requirements — rather than jumping to solutions or surface-level suggestions.

| Scenario Type | Count | Score | Avg Latency |
|---------------|-------|-------|-------------|
| Sales discovery (first calls, BANT gaps, workarounds, magic-wand) | 5 | 98% | 1744ms |
| Customer success (QBR expansion, workarounds, disengaged renewal) | 3 | 94% | 1523ms |
| Product / user research (vague feedback, unused features, manual processes) | 3 | 100% | 1535ms |
| Interviews (technical depth, behavioral probing, collaboration dodge) | 5 | 92% | 1785ms |
| Context density tiers (directive-only through rich context) | 3 | 99% | 1646ms |
| Discovery-to-execution transitions (BANT complete, partial gaps) | 2 | 96% | 1797ms |
| Edge: very early call, minimal transcript | 1 | 94% | 1305ms |

**Remaining weak spots:**

- [major] Interview depth — one technical-probe scenario at 78%. LLM judge is stricter on what counts as "probing deeper" than the underlying keyword assertions.
- [major] Compelling-event probing — one scenario at 91%. Model asked about ideal outcomes instead of what's driving the evaluation. Keyword assertion too narrow for valid alternative phrasings.
- [major] Disengaged-renewal detection — 83% on the customer-success renewal scenario when tension is text-only without acoustic signals.

### Interview Depth

**3 scenarios** | **19/20 assertions** | **98% avg composite**

Tests whether the assistant suggests follow-up questions that probe deeper into candidate responses — clarifying vague claims, testing technical depth, or digging into behavioral specifics.

| Scenario | Score | Key Behavior |
|----------|-------|-------------|
| :white_check_mark: System design — textbook answer, misses trade-offs | 100% | Probes exactly-once gap, data residency contradiction, suggests poison pill and backpressure |
| :white_check_mark: Behavioral — deflects on conflict, vague impact | 93% | Targets vague metrics ("ask for specific cycle time post-PIP") |
| :white_check_mark: Strong depth, dodges collaboration | 100% | Probes bypass-vs-delegation pattern, fires interpersonal on defensiveness |

### Context Density Tiers

Tests whether the minimal one-line template directive produces useful results without any additional context.

| Context Level | Composite | Notes |
|--------------|-----------|-------|
| Directive only (no name, no company) | 100% | Discovery-oriented talking points with zero user input |
| Directive + minimal context | 96% | Mostly solid; occasional minor gaps |
| Directive + rich context (role, status, gaps) | 100% | Budget/authority gaps surfaced from context |
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

**28 scenarios** | **143/157 assertions** | **97% avg composite** | **1,619ms avg latency**

Tests whether the assistant tracks stated goals, surfaces unaddressed items at wrap-up, and drives toward commitments in late-stage meetings.

| Scenario Type | Count | Score | Avg Latency |
|---------------|-------|-------|-------------|
| Goal tracking (budget/timeline coverage, partial completion) | 3 | 100% | 1650ms |
| Wrap-up resurfacing (unaddressed goals at meeting end) | 5 | 100% | 1346ms |
| Complex domain-specific (sales, sprint, QBR, board, partner, attribution) | 6 | 93% | 2060ms |
| Execution-specific (closing, board decisions, standup) | 3 | 100% | 1447ms |
| Standup & blocker ownership (unowned, stalled, minimal) | 3 | 93% | 1697ms |
| Presentation coverage tracking | 4 | 98% | 1426ms |
| Discovery-to-execution transitions | 2 | 94% | 1669ms |
| Long meetings with compacted summary | 1 | 94% | 1570ms |
| Context tier (execution directive only) | 1 | 100% | 1274ms |

**Remaining weak spots:**

- [major] Complex scenarios with dense multi-threaded content — one API-integration partnership scenario at 82% (diagnostic-tool next-step surfaced in 3/5 runs).
- [major] Complex attribution dispute — 88%; Friday deadline occasionally not surfaced.
- [major] Minimal-standup scenario — 82%; model generates filler talking points when nothing needs flagging.
- [major] Presentation "all points covered" — 95%; model occasionally produces transitional bullets instead of minimal output.

### Standup & Blocker Ownership

**3 scenarios** | **~93% avg composite**

Tests detection of unowned blockers and stalled handoffs in standup meetings.

| Scenario | Score | Key Behavior |
|----------|-------|-------------|
| :white_check_mark: Multiple blockers — some owned, some not | 96% | Catches unowned blockers; bullet count mostly within limit |
| :white_check_mark: Stalled handoffs with false-positive non-blockers | 100% | Flags auth keys and PR review; correctly ignores non-blocker noise |
| :large_orange_diamond: Everything on track — minimal expected | 82% | Generates filler talking points when nothing needs flagging |

### Customer Workaround Detection

**3 scenarios** | **100% avg composite**

Tests detection of workarounds and unexpressed needs in customer calls.

| Scenario | Score | Key Behavior |
|----------|-------|-------------|
| :white_check_mark: Spreadsheet workaround normalized as "just how we do it" | 100% | "Ask what Mateo's ideal automated workflow looks like" — connects ETL bottleneck to stalled ML model and European expansion |
| :white_check_mark: Frustrated customer masking pain behind "it's fine" | 100% | Surfaces parallel routing need, Janelle's spreadsheet, compliance risk. Fires interpersonal on "stopped asking" frustration |
| :white_check_mark: Happy customer with buried dependency risk | 100% | Catches Raj single-point-of-failure, suggests exploring native connectors |

### Presentation Coverage Tracking

**4 scenarios** | **98% avg composite**

Tests whether the assistant tracks prepared key points and surfaces uncovered ones.

| Scenario | Score | Key Behavior |
|----------|-------|-------------|
| :white_check_mark: Mid-talk — 2 of 4 points covered | 100% | Surfaces briefing latency and SSO (uncovered); does NOT re-surface ASR or diarization (covered) |
| :white_check_mark: Audience Q&A mid-presentation | 100% | Fires question detection, surfaces SOC 2 and encryption keys (uncovered) |
| :large_orange_diamond: All points covered — minimal expected | 95% | Produces mostly transitional bullets; occasional filler |
| :white_check_mark: Dense financial metrics | 98% | Numbers perfectly preserved; surfaces runway and hiring (uncovered) |

### Wrap-up

**5 scenarios** | **100% avg composite**

| Scenario | Score | Key Behavior |
|----------|-------|-------------|
| :white_check_mark: Unaddressed budget (closing signals) | 100% | Budget surfaced as first bullet |
| :white_check_mark: Two goals unaddressed, meeting ending | 100% | CTO meeting and sign-off both surfaced |
| :white_check_mark: All goals met — no false resurfacing | 100% | No pricing reminder (confirmed); clean minimal output |
| :white_check_mark: Conditional agreement (pending CISO) | 100% | Security review blocker surfaced |
| :white_check_mark: Vague verbal yes without specifics | 100% | Finance approval and timeline gaps surfaced |

## Interpersonal Awareness

**12 scenarios** | **42/48 assertions** | **94% avg composite**

_(Last measured 2026-04-12 — numbers unchanged pending full-suite re-run.)_

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

_(Last measured 2026-04-12 — numbers unchanged pending full-suite re-run.)_

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

_(Last measured 2026-04-12 — numbers unchanged pending full-suite re-run.)_

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

_(Last measured 2026-04-12 — numbers unchanged pending full-suite re-run.)_

Previous items preserved when transcript is unrelated, deadlines updated without duplication, cancelled items removed, aged-out items retained when supported by compacted summary.

## Timezone Resolution

**7 scenarios** | **18/18 assertions** | **100% avg composite**

_(Measured 2026-04-22 after the `dueTimezone` feature landed.)_

Action items carry a `dueTimezone` field (IANA identifier or null). It's resolved from location cues attached to the item's owner — either in USER_CONTEXT prep notes ("Marty is East Coast") or in the transcript itself ("our London office", "by 2 PM Eastern"). When no cue is present for the owner, the field stays null rather than being guessed.

| Scenario Type | Count | Score | Avg Latency | Stability |
|---------------|-------|-------|-------------|-----------|
| USER_CONTEXT cue → resolved zone | 1 | 100% | 1371ms | 82% |
| Transcript cue → resolved zone | 1 | 100% | 1471ms | 78% |
| No location cue → null (no spurious guess) | 1 | 100% | 1298ms | 82% |
| Mixed: owner-scoped zones, user null + remote resolved | 1 | 100% | 1274ms | 79% |
| Attribution: cue about non-committer must not spill over | 1 | 100% | 1437ms | 80% |
| Multi-zone: three speakers, three zones, each independent | 1 | 100% | 1315ms | 87% |
| Explicit zone in commitment speech (no inference needed) | 1 | 100% | 1246ms | 77% |

Display downstream renders the primary time in the user's local zone and appends the speaker's clock when zones differ — so a deadline spoken at "2 PM Eastern" by a coworker lands on the user's screen as `11:00 AM PDT · 2:00 PM EDT`.

## Long Meetings (90+ min)

**7 scenarios** | **29/32 assertions** | **96% avg composite**

_(Last measured 2026-04-12 — numbers unchanged pending full-suite re-run.)_

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

## Refresh Continuity (New — 2026-04-17)

A production change this month passes the prior briefing's markdown back into the next briefing call as `<PREVIOUS_BRIEFING>`. The model preserves the summary section's bullets verbatim while regenerating talking points and interpersonal observations fresh from the recent transcript.

Tested in an internal multi-turn exploration across 3 long-meeting scenarios (enterprise deal, sprint planning, investor board) with a judge scoring preservation, new-content incorporation, and hallucination against the prior summary:

| Metric | Baseline (no prior state) | With `<PREVIOUS_BRIEFING>` |
|--------|:-:|:-:|
| Summary preservation score (1-5) | 3.0 | **5.0** |
| Dropped bullets per refresh (avg) | 1.7 | **0** |
| Hallucinated facts (avg) | 1.7 | **0** |
| Talking-point freshness (bleed check) | N/A | **No bleed observed** |

The model correctly preserves summary bullets across refreshes while generating fresh talking points from the recent window. This addresses the prior "summary appears one refresh, gone the next" behavior.

## Template Compliance

**2 scenarios** | **12/13 assertions** | **99% avg composite**

_(Last measured 2026-04-12 — numbers unchanged pending full-suite re-run.)_

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

- **96 scenarios**, 5 runs each (480 total briefing API calls for a full suite)
- **Production config**: Gemini 3 Flash at temperature 1.0, thinking=minimal for briefing; Gemini 3.1 Flash Lite at temperature 0.2, thinking=minimal for action items.
- **Deterministic assertions**: string matching, bullet counts, template structure, annotation leakage detection
- **LLM judge**: Claude Sonnet evaluates semantic quality (hallucination, grounding, forward-looking, discovery depth, interview depth, blocker ownership, workaround detection, presentation coverage, requirements surfacing)
- **Composite scoring**: Critical assertions weighted 3x, Major 2x, Minor 1x
- **Stability**: measured by bullet count variance and keyword Jaccard similarity across runs

See the [benchmark README](../README.md) for full assertion type documentation.
