# Meeting Assistant Benchmark Results

**Date:** 2026-04-08T18:34:50Z
**Briefing model:** gemini-3-flash-preview (thinking=minimal)
**Action items model:** gemini-3.1-flash-lite-preview (thinking=minimal)
**Judge:** Claude sonnet
**Runs per scenario:** 3

## Summary

| Metric | Value |
|--------|-------|
| Scenarios | 53 |
| Assertions passed | 204 / 221 (92%) |
| **Composite score** | **94.4%** |
| Avg latency | 1664ms |
| p50 / p95 / p99 latency | 1647ms / 2342ms / 2587ms |
| Stability | 88% avg |
| Action items extracted | 160 (125 with due dates) |
| Action items avg latency | 2187ms |

## Goal Tracking & Forward-Looking

**9 scenarios** | **41/44 assertions** | **95% avg composite**

| Scenario | Score | Assertions | Latency | Stability |
|----------|-------|------------|---------|-----------|
| :white_check_mark: Goal: budget never discussed (30-min call) | 100% | 4/4 | 1931ms | 83% |
| :large_orange_diamond: Goal: both budget and timeline covered | 85% | 4/5 | 1807ms | 91% |
| :white_check_mark: Goal: timeline discussed, budget missing (mid-call) | 100% | 4/4 | 1604ms | 91% |
| :large_orange_diamond: Forward-looking: don't parrot recent exchange | 70% | 3/5 | 1619ms | 87% |
| :white_check_mark: Forward-looking: suggest what hasn't been covered | 100% | 4/4 | 1644ms | 85% |
| :white_check_mark: Wrap-up: unaddressed budget goal with closing signals (should be first bullet) | 100% | 5/5 | 1348ms | 91% |
| :white_check_mark: Wrap-up: two goals unaddressed, meeting ending abruptly | 100% | 5/5 | 1373ms | 89% |
| :white_check_mark: Wrap-up: all goals met, no false resurfacing | 100% | 4/4 | 1454ms | 88% |
| :white_check_mark: Long meeting: compacted summary + recent window, quality stable | 100% | 8/8 | 1825ms | 86% |

**Failures:**

- [0%] [major] Forward-looking: don't parrot recent exchange -- No parroting 'native connectors' in talking points
- [33%] [major] Goal: both budget and timeline covered -- No budget reminder (goal met)
- [67%] [major] Forward-looking: don't parrot recent exchange -- No parroting 'migration support' in talking points

## Interpersonal Awareness

**12 scenarios** | **47/48 assertions** | **98% avg composite**

| Scenario | Score | Assertions | Latency | Stability |
|----------|-------|------------|---------|-----------|
| :white_check_mark: Interpersonal: overlap during disagreement (annotated) | 100% | 5/5 | 1639ms | 81% |
| :white_check_mark: Interpersonal: overlap during disagreement (baseline, no annotations) | 100% | 3/3 | 1853ms | 92% |
| :white_check_mark: Interpersonal: fast speech during pricing pushback (annotated) | 100% | 4/4 | 1950ms | 85% |
| :white_check_mark: Interpersonal: combined overlap + fast during heated exchange (annotated) | 100% | 4/4 | 1986ms | 79% |
| :white_check_mark: Interpersonal: neutral conversation, no annotations | 100% | 3/3 | 1849ms | 83% |
| :white_check_mark: Interpersonal: overlap during enthusiastic agreement | 100% | 4/4 | 1469ms | 92% |
| :white_check_mark: Edge: passive agreement with tension acoustic signals | 100% | 4/4 | 1644ms | 81% |
| :white_check_mark: Edge: fast technical explanation — no tension (false positive risk) | 100% | 4/4 | 1507ms | 100% |
| :white_check_mark: Edge: excited fast speech on good news — no negative signal | 100% | 5/5 | 1933ms | 95% |
| :large_orange_diamond: Edge: brief overlap at natural turn boundaries | 71% | 3/4 | 1556ms | 85% |
| :white_check_mark: Edge: pervasive overlaps in collaborative working session | 100% | 4/4 | 1402ms | 100% |
| :white_check_mark: Edge: text-only disagreement without acoustic signals (regression test) | 100% | 4/4 | 1779ms | 86% |

**Failures:**

- [0%] [major] Edge: brief overlap at natural turn boundaries -- No interpersonal flag for natural turn overlaps

## Complex Scenarios

**7 scenarios** | **33/43 assertions** | **84% avg composite**

| Scenario | Score | Assertions | Latency | Stability |
|----------|-------|------------|---------|-----------|
| :white_check_mark: Complex: enterprise data observability deal, multi-product with competitor eval | 100% | 6/6 | 1749ms | 87% |
| :x: Complex: sprint planning with internal tools, feature scoping, and infra migration | 70% | 4/6 | 1852ms | 89% |
| :white_check_mark: Complex: hiring committee debrief with rubric scores and bar-raiser veto | 100% | 5/5 | 1916ms | 88% |
| :large_orange_diamond: Complex: QBR with product issues, trust erosion, and gated expansion | 90% | 5/7 | 2364ms | 75% |
| :x: Complex: API integration partnership with hybrid deployment constraints | 58% | 3/6 | 1947ms | 91% |
| :large_orange_diamond: Complex: Series B board prep with CFO, bridge round debate, margin tension | 79% | 4/6 | 2687ms | 78% |
| :large_orange_diamond: Complex: attribution dispute, channel budget allocation with competing data | 90% | 6/7 | 1947ms | 78% |

**Failures:**

- [0%] [major] Complex: sprint planning with internal tools, feature scoping, and infra migration -- Surfaces Elliot communication (decided to cut Constellation)
- [0%] [major] Complex: API integration partnership with hybrid deployment constraints -- Max 3 talking points
- [0%] [major] Complex: API integration partnership with hybrid deployment constraints -- No summarization as talking points (LLM judge)
- [0%] [major] Complex: Series B board prep with CFO, bridge round debate, margin tension -- Max 3 talking points
- [33%] [major] Complex: sprint planning with internal tools, feature scoping, and infra migration -- No summarization as talking points (LLM judge)
- [33%] [major] Complex: attribution dispute, channel budget allocation with competing data -- Surfaces Sam's model by Friday (next step)
- [67%] [major] Complex: QBR with product issues, trust erosion, and gated expansion -- Max 3 talking points
- [67%] [major] Complex: QBR with product issues, trust erosion, and gated expansion -- No summarization as talking points (LLM judge)
- [67%] [major] Complex: API integration partnership with hybrid deployment constraints -- Surfaces diagnostic tool action (next step)
- [67%] [minor] Complex: Series B board prep with CFO, bridge round debate, margin tension -- Latency <= 3000ms

## Question Detection

**7 scenarios** | **18/19 assertions** | **93% avg composite**

| Scenario | Score | Assertions | Latency | Stability |
|----------|-------|------------|---------|-----------|
| :white_check_mark: Question: unanswered Remote question at end of transcript | 100% | 3/3 | 1348ms | 98% |
| :white_check_mark: Question: Remote question answered by user — should not surface | 100% | 3/3 | 1356ms | 80% |
| :white_check_mark: Question: Remote question answered by another Remote — should not surface | 100% | 3/3 | 1392ms | 90% |
| :white_check_mark: Question: user asks question, gets answer — must NOT surface | 100% | 2/2 | 1360ms | 94% |
| :white_check_mark: Question: user asks multiple questions, all answered — no question surfaced | 100% | 3/3 | 1432ms | 92% |
| :x: Question: Remote deflects without answering — question should surface | 50% | 1/2 | 1713ms | 85% |
| :white_check_mark: Question: rhetorical Remote question — should not surface | 100% | 3/3 | 1560ms | 87% |

**Failures:**

- [33%] [critical] Question: Remote deflects without answering — question should surface -- Question detection correct (LLM judge)

## Action Items

**4 scenarios** | **13/14 assertions** | **97% avg composite**

| Scenario | Score | Assertions | Latency | Stability |
|----------|-------|------------|---------|-----------|
| :large_orange_diamond: Action items: explicit commitments with due dates (sales call) | 89% | 3/4 | 1639ms | 93% |
| :white_check_mark: Action items: brainstorming should NOT produce items | 100% | 3/3 | 1473ms | 93% |
| :white_check_mark: Action items: mixed commitments and vague plans (should extract only commitments) | 100% | 4/4 | 1829ms | 90% |
| :white_check_mark: Action items: no commitments in casual check-in (should return empty) | 100% | 3/3 | 1493ms | 88% |

**Failures:**

- [67%] [critical] Action items: explicit commitments with due dates (sales call) -- Due dates grounded in transcript (LLM judge)

## Incremental Action Items

**5 scenarios** | **11/11 assertions** | **100% avg composite**

| Scenario | Score | Assertions | Latency | Stability |
|----------|-------|------------|---------|-----------|
| :white_check_mark: Action items: incremental — previous items preserved with new transcript | 100% | 2/2 | 1364ms | 90% |
| :white_check_mark: Action items: incremental — transcript updates deadline on existing item | 100% | 3/3 | 1531ms | 92% |
| :white_check_mark: Action items: incremental — unrelated new transcript, all previous items preserved | 100% | 2/2 | 1337ms | 86% |
| :white_check_mark: Action items: incremental with compacted summary — aged-out items retained | 100% | 2/2 | 1656ms | 84% |
| :white_check_mark: Action items: incremental — transcript cancels a previous item | 100% | 2/2 | 1524ms | 90% |

## Long Meetings

**5 scenarios** | **21/22 assertions** | **98% avg composite**

| Scenario | Score | Assertions | Latency | Stability |
|----------|-------|------------|---------|-----------|
| :white_check_mark: Long: company all-hands (8 speakers, 90 min) | 100% | 4/4 | 1651ms | 98% |
| :white_check_mark: Long: enterprise deal negotiation (90 min, 3 speakers) | 100% | 4/4 | 2112ms | 86% |
| :white_check_mark: Long: product sprint planning (90 min, eng team) | 100% | 4/4 | 1866ms | 87% |
| :white_check_mark: Long: investor board update with CFO tension (90 min) | 100% | 4/4 | 1751ms | 94% |
| :large_orange_diamond: Long meeting: earlier decisions in summary should not be re-suggested | 88% | 5/6 | 1530ms | 84% |

**Failures:**

- [33%] [major] Long meeting: earlier decisions in summary should not be re-suggested -- Does NOT re-suggest Lighthouse P0 (already decided)

## Template Compliance

**2 scenarios** | **13/13 assertions** | **100% avg composite**

| Scenario | Score | Assertions | Latency | Stability |
|----------|-------|------------|---------|-----------|
| :white_check_mark: Template: question detected, full structure expected | 100% | 6/6 | 1532ms | 91% |
| :white_check_mark: Template: no question, no interpersonal — minimal structure | 100% | 7/7 | 1613ms | 85% |

## Other

**2 scenarios** | **7/7 assertions** | **100% avg composite**

| Scenario | Score | Assertions | Latency | Stability |
|----------|-------|------------|---------|-----------|
| :white_check_mark: Edge: very early call, minimal transcript | 100% | 4/4 | 992ms | 89% |
| :white_check_mark: Edge: no prepared context | 100% | 3/3 | 1503ms | 89% |

