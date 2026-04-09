# Meeting Assistant Benchmark

Evaluates the real-time meeting assistant briefing system in [MimicScribe](https://mimicscribe.app). The assistant generates talking points, action items, question detection, and interpersonal awareness suggestions during live meetings.

96 scenarios are run 5 times each against the production prompt. Each run is scored by a combination of deterministic assertions and LLM-as-judge (Claude Sonnet) semantic evaluation.

## Models

| Call | Model | Thinking | Purpose |
|------|-------|----------|---------|
| Briefing | Gemini 3 Flash | minimal | Talking points, summary, question detection, interpersonal |
| Action items | Gemini 3.1 Flash Lite | minimal | Structured JSON extraction |
| Judge | Claude Sonnet | — | LLM-as-judge for semantic assertions |

## What's Tested

### Hallucination (6 scenarios)

Targeted tests for specific hallucination failure modes:

- **Prepared context bleeding**: Internal notes (e.g., "Laura was previously at Snowflake — use this to build rapport") must not surface as talking points when the conversation hasn't touched the topic
- **Number/date mutation**: Dense financial transcripts with many similar numbers ($48K, $62K, $35K, $180K). Every number in the output must exactly match a source.
- **Speaker name fabrication**: Anonymous remote participants must not be given invented names. Generic references ("the prospect", "the client") are required when no name is available.
- **Similar numbers across topics**: Multi-product pricing discussions where numbers could be confused across products (e.g., $24/seat vs $15/monitor vs $850/month).
- **Partial transcript**: Early meetings with minimal context. The model must not fill gaps with plausible-sounding fabricated details.
- **Competitor context**: Prepared context mentions a competitor (e.g., "They evaluated Otter.ai") but the transcript doesn't. The model should not surface competitor names unless the conversation creates an opening.

### Goal Tracking (13 scenarios)

Verifies the assistant surfaces unaddressed meeting goals as talking points. Tests partial coverage (timeline discussed but budget missing), full coverage (no false reminders), and end-of-meeting resurfacing when goals are still open.

### Interpersonal Awareness (12 scenarios)

Tests detection of tension, defensiveness, and disengagement from transcript text and acoustic signals (overlap, speech rate, response latency). Equally important: verifies the assistant does NOT flag positive dynamics — enthusiasm, collaborative overlaps, fast technical discussion, and natural turn-taking are not interpersonal risks.

Acoustic signals are passed in a separate `<ACOUSTIC_SIGNALS>` block (not inlined in the transcript) to prevent raw annotation terms from leaking into the output.

### Action Items (13 scenarios)

Tests extraction of explicit commitments ("I will", "I'll send") with owner and due date. Verifies brainstorming ("we should", "we could") and casual suggestions do not produce action items. Due dates are checked against transcript time references.

Incremental scenarios (9 of 13) test the `<PREVIOUS_ACTION_ITEMS>` mechanic:

- Previous items preserved when transcript is unrelated
- Deadlines updated when transcript refines them (no duplicate created)
- Cancelled items removed when transcript explicitly cancels
- Aged-out items retained when supported by compacted meeting summary
- New items added alongside preserved ones

### Question Detection (7 scenarios)

Only questions from remote speakers are surfaced. Questions asked by the user are excluded. A question is considered answered if any subsequent speaker addresses it. Tests unanswered questions, answered questions, multi-party answers, rhetorical questions, and deflection.

### Interview Depth (5 scenarios)

Tests whether the assistant suggests follow-up questions that probe deeper into candidate responses — clarifying vague claims, testing technical depth, exploring specifics behind generalizations, or digging into behavioral examples. Includes system design interviews where candidates give textbook answers without failure modes, behavioral rounds where candidates deflect on conflict or give vague impact claims, and collaboration assessments where candidates default to solo execution.

### Standup & Blocker Ownership (4 scenarios)

Tests detection of unowned blockers and stalled handoffs in standup meetings. Multi-blocker scenarios with a mix of owned and unowned items verify the assistant flags the right things (unassigned tickets, unclaimed requests) while not flagging items that clearly have owners and are progressing. Includes edge cases where everything is on track and minimal talking points are expected.

### Customer Workaround Detection (3 scenarios)

Tests detection of workarounds (manual processes, custom scripts, spreadsheet hacks) and unexpressed needs in customer calls. Long transcripts where customers describe elaborate workarounds as normal ("we just do X") rather than as problems. Includes a frustrated customer masking pain behind "it's fine," an elaborate ETL pipeline workaround blocking three initiatives, and a happy customer with a buried single-point-of-failure dependency.

### Presentation Coverage Tracking (4 scenarios)

Tests whether the assistant tracks prepared talking points and surfaces uncovered ones during presentations. The user lists key points in their prepared context, then delivers some but not all during the talk. The assistant should surface remaining points without re-surfacing covered ones. Includes mid-talk coverage, audience Q&A handling, all-points-covered edge case, and dense financial metrics with number preservation.

### Complex Scenarios (7 scenarios)

Long domain-specific transcripts with jargon (enterprise sales, sprint planning, board meetings, QBR). Tests hallucination (no fabricated names/numbers), forward-looking talking points (not recaps), and domain term preservation.

### Long Meetings (5 scenarios, 90+ min simulated)

Simulates 90+ minute meetings using a compacted summary (~300 words representing the first 70-80 minutes), a recent transcript window (~400 words), and accumulated previous action items. Includes an 8-speaker company all-hands, enterprise deal negotiation, sprint planning, and investor board update.

### Template Compliance (2 scenarios)

Verifies output structure: question line before bullets, interpersonal before divider, summary after divider. No markdown headers, bold formatting on names/numbers, bullet length limits.

## Scoring

**Composite score**: Weighted average across all assertions per scenario.

| Weight | Multiplier | Used for |
|--------|-----------|----------|
| Critical | 3x | Hallucination, action item stability |
| Major | 2x | Goal tracking, forward-looking, interpersonal accuracy |
| Minor | 1x | Template compliance, latency |

**Stability**: Structural consistency across 5 runs — bullet count variance and keyword overlap (Jaccard similarity).

## Assertion Types

### Deterministic

Exact checks that don't require judgment: string presence/absence, bullet counts, template structure ordering, annotation leakage detection, backward-looking phrase detection.

### LLM Judge (Claude Sonnet)

Semantic evaluation where interpretation is required:

| Rubric | What it evaluates |
|--------|-------------------|
| Hallucination | No fabricated names, numbers, dates, or claims beyond all provided context |
| No Fabricated Names | Speaker names in output must trace to a source; generic references required for unnamed speakers |
| Numbers Preserved | Every number, price, percentage, and date exactly matches a source (formatting changes OK) |
| No Summarization | Talking points propose forward actions, not recaps of what was said |
| Action Items Grounded | Every item traces to an explicit verbal commitment |
| Due Dates Grounded | Every due date maps to a time reference in the transcript |
| Action Items Stable | Previous items preserved unless transcript supersedes; no duplicates |
| Question Detection | Only unanswered remote questions surfaced; user's own questions excluded |
| Interview Depth | Follow-ups probe vague claims, test technical depth, or dig into behavioral specifics |
| Blocker Ownership | Unowned blockers and stalled handoffs flagged; owned items not falsely flagged |
| Workaround Detection | Workarounds and unexpressed needs surfaced; cost/frequency explored |
| Presentation Coverage | Uncovered prepared points surfaced; covered points not re-surfaced |

## Results

See [results/RESULTS.md](results/RESULTS.md).
