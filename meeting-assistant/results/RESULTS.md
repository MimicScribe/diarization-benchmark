# Meeting Assistant Benchmark Results

Pipeline: Gemini 3 Flash (briefing) + Gemini 3.1 Flash Lite (action items) + Claude Sonnet (judge)

Run date: 2026-04-08 | 81 scenarios | 3 runs each

## Summary

| Metric | Value |
|--------|-------|
| Scenarios | 81 |
| Assertions passed | 306 / 340 |
| **Composite score** | **95.5%** |
| Avg latency | 1665ms |
| p50 / p95 / p99 latency | 1598ms / 2156ms / 3248ms |
| Stability (cross-run consistency) | 89% avg |
| Action items extracted | 161 (127 with due dates) |

## Hallucination (Targeted)

**6 scenarios** | **25/27 assertions** | **96% avg composite**

| Scenario | Score | Assertions | Latency | Stability |
|----------|-------|------------|---------|-----------|
| :white_check_mark: Prepared context bleeding into summary | 100% | 6/6 | 1707ms | 97% |
| :white_check_mark: Number/date mutation in dense financial discussion | 100% | 4/4 | 1608ms | 88% |
| :white_check_mark: Speaker name fabrication (anonymous participants) | 100% | 5/5 | 1695ms | 86% |
| :white_check_mark: Similar numbers across topics (confusion risk) | 100% | 4/4 | 1426ms | 92% |
| :white_check_mark: Partial transcript with sparse context | 100% | 4/4 | 1504ms | 92% |
| :large_orange_diamond: Competitor in context but not in transcript | 78% | 2/4 | 1882ms | 86% |

**Failures:**

- [67%] [critical] Competitor context scenario — model sometimes surfaces competitor name from prepared context even when the transcript doesn't mention it

## Discovery Quality

**19 scenarios** | **90/93 assertions** | **98% avg composite**

Tests whether the assistant helps users understand the other party's situation — root causes, ideal outcomes, impact quantification, and unexplored requirements — rather than jumping to solutions or surface-level suggestions.

| Scenario Type | Count | Score | Avg Latency | Stability |
|---------------|-------|-------|-------------|-----------|
| Sales discovery (first calls, BANT gaps, workarounds) | 8 | 97% | 1575ms | 88% |
| Customer success (QBR expansion, workarounds, renewal) | 3 | 97% | 1577ms | 92% |
| User research (vague feedback, unused features, manual processes) | 3 | 100% | 1542ms | 89% |
| Interviews (technical depth, motivation probing) | 2 | 100% | 1605ms | 87% |
| Context density tiers (directive-only through rich context) | 3 | 100% | 1548ms | 89% |

**Failures:**

- [33%] [major] Compelling event scenario — model asked about ideal outcomes instead of what's driving the evaluation. LLM judge still passed for discovery quality; the keyword assertion was too narrow.
- [67%] [major] Renewal with disengagement signals — model correctly detected disengagement in the interpersonal line but 1/3 runs didn't surface it in talking point keywords.
- [0%] [major] Name from context not used — model was given a name in the prepared context but didn't apply it to the [Remote] speaker. Known limitation with minimal context.

### Context Density Tiers

Tests whether the minimal one-line template directive produces useful results without any additional context.

| Context Level | Composite | Notes |
|--------------|-----------|-------|
| Directive only (no name, no company) | 100% | Discovery-oriented talking points with zero user input |
| Directive + name and company | 100% | Same quality; model did not use the provided name |
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

**Impact quantification** — prospect says "our reports are always wrong":
> - Ask what's driving the **two-day** reconciliation delay.
> - Ask how much time **Finance** and **Ops** waste monthly.

**Ideal-state probing** — customer describes 45-minute daily reconciliation:
> - Ask what an **ideal automated solution** would look like.

**BANT gap surfacing** — 20 minutes of technical discussion, budget never mentioned:
> - Ask who else needs to approve the **Q4** budget.

**Interview depth** — candidate gives high-level caching answer without failure modes:
> - Ask how they would handle **hot keys** specifically.
> - Ask about **cache stampede** prevention for expired keys.

## Execution Quality (Goal & Commitment Tracking)

**19 scenarios** | **94/99 assertions** | **97% avg composite**

Tests whether the assistant tracks stated goals, surfaces unaddressed items at wrap-up, and drives toward commitments in late-stage meetings.

| Scenario Type | Count | Score | Avg Latency | Stability |
|---------------|-------|-------|-------------|-----------|
| Goal tracking (budget/timeline coverage, partial completion) | 3 | 100% | 1606ms | 89% |
| Wrap-up resurfacing (unaddressed goals at meeting end) | 3 | 97% | 1483ms | 89% |
| Complex domain-specific (sales, sprint, QBR, board, partner) | 6 | 83% | 2052ms | 84% |
| Execution-specific (closing, standup blockers, board decisions) | 4 | 100% | 1521ms | 87% |
| Discovery-to-execution transition | 2 | 95% | 1681ms | 85% |
| Long meetings with compacted summary | 1 | 100% | 1872ms | 87% |

**Failures:**

- [0%] [major] Complex partner scenario — model failed to surface the immediate next-step action item (diagnostic tool), focusing instead on confirming prior decisions
- [33%] [major] Complex sprint planning — team member communication commitment surfaced in only 1/3 runs
- [33%] [major] Complex attribution dispute — missed surfacing the Friday deadline for the attribution model
- [67%] [major] Wrap-up with all goals met — false positive pricing reminder in 1/3 runs despite pricing being confirmed
- [67%] [major] Discovery-to-execution transition — continued asking discovery questions in 1/3 runs after requirements were fully gathered

## Interpersonal Awareness

**12 scenarios** | **44/48 assertions** | **96% avg composite**

| Scenario Type | Count | Score | Avg Latency | Stability |
|---------------|-------|-------|-------------|-----------|
| Tension detection with acoustic signals | 3 | 98% | 2023ms | 85% |
| Tension detection from text only | 1 | 90% | 1802ms | 78% |
| False positive suppression (enthusiasm, collaboration, technical speed) | 5 | 97% | 1662ms | 90% |
| Acoustic signal edge cases (disengagement, natural overlap) | 3 | 90% | 1826ms | 89% |

**Failures:**

- [0%] [major] Natural turn-boundary overlaps — model incorrectly flagged brief collaborative overlaps as interpersonal risk
- [67%] [major] Text-only disagreement — tension detected in 2/3 runs without acoustic signals (acceptable but inconsistent)
- [67%] [minor] Two scenarios exceeded 3000ms latency target on individual runs

## Question Detection

**7 scenarios** | **18/19 assertions** | **89% avg composite**

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

**4 scenarios** | **13/14 assertions** | **97% avg composite**

| Scenario Type | Count | Score | Avg Latency |
|---------------|-------|-------|-------------|
| Explicit commitments with due dates | 1 | 89% | 1653ms |
| Brainstorming rejection (no phantom items) | 1 | 100% | 1425ms |
| Mixed commitments and vague plans | 1 | 100% | 1580ms |
| No commitments (casual check-in) | 1 | 100% | 1330ms |

**Failures:**

- [67%] [critical] Due date grounding — one date resolved to the wrong day in 1/3 runs

## Incremental Action Items

**5 scenarios** | **10/11 assertions** | **99% avg composite**

Previous items preserved when transcript is unrelated, deadlines updated without duplication, cancelled items removed, aged-out items retained when supported by compacted summary.

**Failures:**

- [67%] [minor] One scenario exceeded latency target on a single run

## Long Meetings (90+ min)

**5 scenarios** | **19/22 assertions** | **93% avg composite**

| Scenario Type | Count | Score | Avg Latency | Stability |
|---------------|-------|-------|-------------|-----------|
| Multi-speaker all-hands (8 speakers) | 1 | 89% | 1702ms | 93% |
| Enterprise deal negotiation | 1 | 100% | 1684ms | 87% |
| Sprint planning continuation | 2 | 94% | 1580ms | 85% |
| Investor board update | 1 | 89% | 1744ms | 85% |

**Failures:**

- [67%] [critical] Two long-meeting scenarios — hallucination on financial details (names or numbers slightly mutated) in dense multi-speaker sessions
- [33%] [major] Sprint continuation — model re-suggested a decision that was already settled in the compacted summary

## Template Compliance

**2 scenarios** | **13/13 assertions** | **100% avg composite**

Output structure (question before bullets, interpersonal before divider, summary after divider), bold formatting, and bullet length limits all pass consistently.

## Methodology

- **81 scenarios**, 3 runs each (243 total briefing API calls)
- **Deterministic assertions**: string matching, bullet counts, template structure, annotation leakage detection
- **LLM judge**: Claude Sonnet evaluates semantic quality (hallucination, grounding, forward-looking, discovery depth, requirements surfacing)
- **Composite scoring**: Critical assertions weighted 3x, Major 2x, Minor 1x
- **Stability**: measured by bullet count variance and keyword Jaccard similarity across runs

See the [benchmark README](../README.md) for full assertion type documentation.
