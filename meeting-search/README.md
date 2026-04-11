# Meeting Search Benchmark

Evaluates the meeting vector search pipeline: how accurately MimicScribe retrieves the correct meeting when users search across months of transcribed conversations. Tests whether specific details buried deep in long, dense meetings can be found through natural language queries.

## What It Tests

Every meeting generates a set of on-device embedding vectors from its title, summary, search phrases, and action items. When users search, the query is embedded and matched against all meeting vectors via cosine similarity. The benchmark measures whether the correct meeting ranks in the top results.

The corpus contains 26 meetings across a realistic range of lengths and complexity:

- **Marathon meetings (90+ min)**: 8 meetings ranging from 90 minutes to 5 hours — quarterly business reviews, architecture reviews, customer advisory boards, incident post-mortems, sales kickoffs, board meetings, product planning sessions. Summaries range from 780 to 1,127 words with 6-10 distinct topics each.
- **Standard meetings (30-60 min)**: 10 meetings — sprint planning, customer demos, marketing reviews, hiring debriefs, security audits, design reviews, partner kickoffs.
- **Short meetings (15-30 min)**: 8 meetings — daily standups, quick syncs, bug triages, 1:1s.

138 search queries across 8 types test different ways users find meetings:

| Query type | Count | What it tests |
|-----------|------:|---------------|
| Topic | 11 | Direct topic match ("quarterly revenue review") |
| Buried | 65 | Specific detail deep in a long meeting ("viewer seat pricing eight dollars read-only users") |
| Disambiguation | 24 | Right meeting when multiple discuss the same topic (APAC expansion in 3 different meetings) |
| Conversational | 10 | Casual phrasing ("that meeting where we talked about the database being slow") |
| Action item | 8 | Specific task or owner ("who's responsible for the Snowflake connector") |
| Decision | 6 | Outcome queries ("who did we decide to hire for the SRE role") |
| Person | 6 | Participant or company name ("meetings with Pinnacle Insurance") |
| Vague | 8 | Ambiguous queries matching multiple meetings ("pricing discussion") |

One meeting includes realistic ASR pipeline artifacts — diarization errors, garbled jargon, imprecise numbers, thin sections from cross-talk — to test robustness against noisy input.

## Embedding Strategies Compared

The benchmark compares 7 embedding strategies to measure how vector count and phrasing style affect retrieval:

| Strategy | Vectors/meeting | Description |
|----------|----------------:|-------------|
| Formal (old) | ~6 | Title + full summary + 3-5 formal descriptions + concatenated action items |
| Conversational (hand-crafted) | ~45 | Title + summary + sentences + 8-15 conversational phrases + individual action items |
| Gemini formal | ~7.5 | Same as formal but Gemini generates the descriptions |
| Gemini conversational | ~46 | Same as conversational but Gemini generates the phrases |
| **Gemini production** | **~28** | **Title + summary + paragraphs + Gemini phrases + individual action items (shipped)** |

The production strategy uses summary paragraph splitting (not sentence splitting) as the balance between vector count and retrieval quality.

## Metrics

- **Recall@3 (R@3)**: Is the correct meeting in the top 3 results? Primary metric — the AI answer synthesizer works from the top results.
- **Recall@5 (R@5)**: Is the correct meeting in the top 5? Safety net metric.
- **MRR** (Mean Reciprocal Rank): How high is the correct meeting ranked on average?

## Results

See [results/RESULTS.md](results/RESULTS.md) for the latest benchmark results.
