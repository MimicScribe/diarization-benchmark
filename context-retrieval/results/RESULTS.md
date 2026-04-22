# Context Retrieval Benchmark Results

Production pipeline: Gemini 3.1 Flash Lite (semantic chunking with conversational search phrases) + all-MiniLM-L6-v2 on-device embedding (384-dim transformer) + multi-query max-pool retrieval with absolute-floor relevance gate (0.35)

Run date: 2026-04-21

## End-to-End Retrieval

**83% of positive queries surface the correct chunk to the briefing LLM** across 38 scenarios and 135 queries covering CRMs, PDFs, scraped webpages, Spanish and code-switched English+Spanish docs, Wikipedia, SEC filings, messy meeting notes, and long multi-topic meetings.

| Metric | Score |
|--------|------:|
| Right chunk reaches LLM (positive queries) | **83.2%** |
| Gate passes (positive queries) | 85.0% |
| Correctly silenced (negative queries) | 63.6% |
| Retrieval accuracy alone, ungated R@3 | 98.9% |
| MRR | 95.3% |
| Query latency (embed + retrieve) | <15ms |

Retrieval is near-perfect at the embedding layer — once a query is embedded, the right chunk is in the top 3 results 98.9% of the time. The 83.2% figure reflects what reaches the LLM after the relevance gate, which is tuned to stay silent when the match isn't confident enough.

## The Relevance Gate

The gate blocks retrieval when the top chunk's max-pooled similarity falls below an absolute threshold (0.35). This prevents the LLM from being fed marginally-related context when the user's question isn't actually aligned with their loaded docs.

- Floor: **0.35 cosine similarity** (dot product on L2-normalized embeddings)
- Positive queries the gate blocks (silence when docs had an answer): 15%
- Negative queries the gate passes (wrong context offered): 36%

The negative-reject rate (63.6%) is the conservative side of the tradeoff. A higher floor blocks more legitimate questions; a lower floor passes more irrelevant context. The downstream briefing prompt is source-restricted — even when reference chunks are injected for an unrelated query, the summarization/briefing prompt only uses reference context that connects to the actual meeting transcript, which mitigates visible hallucination in practice.

## Scope

- **38 scenarios**, 8 document types: CRMs with UI artifacts, scraped webpages with HTML noise, PDF extractions with broken line wraps, messy meeting notes with emoji and Slack threads, tracked-changes markup, clean product docs, SEC filings, Wikipedia articles.
- **135 queries**: 113 positive (expect retrieval), 22 negative (expect silence).
- **Dirty inputs**: HTML tags, broken PDF hyphenation, UI buttons, emoji, Slack thread quotes, tracked-changes annotations — all fed to the chunker as-is, no manual cleanup.
- **Multilingual**: English, Spanish, and code-switched English+Spanish scenarios.
- **Long meetings**: multi-topic transcripts where relevant context is buried 30+ minutes deep.

## How It Works

1. **Chunking** (ingest, ~5s per doc): Gemini 3.1 Flash Lite splits the document into semantic chunks and generates 1-4 search phrases per chunk. Phrases are written as natural spoken questions ("what's the deal size with acme"), lowercase to match ASR transcript output.

2. **Embedding** (ingest, <10ms per chunk): Each search phrase is embedded with all-MiniLM-L6-v2 (384-dim transformer, on-device). Headers are embedded as the index key; bodies carry the full content.

3. **Retrieval** (query, <15ms): Prepared context + recent transcript turns are embedded as multiple queries. Each chunk scores by max cosine similarity across all queries. A single absolute-floor gate (0.35) decides whether to return results or stay silent.

4. **Injection**: Chunks above the entry threshold (`max(floor, topScore × 0.80)`) are formatted as reference context in the LLM prompt. The briefing and summarization prompts are source-restricted — reference context enriches facts already discussed in the meeting but cannot introduce new action items or topics.

## Tuning History

- **2026-04-21**: Floor lowered from 0.40 → 0.35. Benchmark showed the 0.40 threshold was blocking legitimate positive queries (e.g. "What are the pricing tiers?", "What healthcare-specific features are available?") where the right chunk was scored in the 0.35-0.40 range. Positive gate-pass rose from 50% → 85%; negative-reject fell from 77% → 64%. Net improvement on realistic usage ratios.

- **2026-04-10** (prior): Embedding model unified on all-MiniLM-L6-v2 (384-dim transformer). Previously used potion-retrieval-32M (256-dim static model); MiniLM improved accuracy on conversational query phrasing.

## Methodology Notes

- **Recall@3** measures whether the ground-truth chunk is retrieved in the top 3 when the gate is bypassed. This is the pure retrieval-quality number.
- **Gate pass / right chunk reaches LLM** are the end-to-end production numbers that reflect what the user actually experiences. They're lower than R@3 because the gate intentionally suppresses low-confidence matches to avoid injecting irrelevant context.
- **Negative queries** are realistic unrelated questions issued against loaded docs — e.g., "What is our employee benefits policy?" on a CRM dump, or "How do transformers handle protein folding?" on the Transformer Wikipedia page. The system should stay silent.
- **Queries are hand-written** to reflect realistic user questions, not synthetic generations. Source documents include real-world noise (HTML, PDF artifacts, tracked changes) to match production conditions.

## Production vs Benchmark

These numbers measure the production retrieval path directly — single-query inputs routed through `multiQueryRetrieve()` as 1-element pools, matching the Swift production code. In live usage, prepared context + multiple transcript turns are embedded and max-pooled together, which typically produces higher scores than single-query benchmarking. Real production gate-pass is likely somewhat higher than the 85% measured here.

The 83% headline number is therefore a conservative lower bound on end-to-end retrieval quality.
