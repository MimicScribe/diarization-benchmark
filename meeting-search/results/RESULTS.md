# Meeting Search Benchmark Results

Pipeline: Gemini 3 Flash (conversational search phrase generation) + all-MiniLM-L6-v2 (on-device transformer embedding, 384-dim) + cosine similarity search with max-aggregation per meeting

Run date: 2026-04-10 | 26 meetings | 138 queries | ~28 vectors per meeting

## Overall

**98% of queries found the correct meeting in the top 3 results.** All 138 queries find the correct meeting in the top 5 (100% R@5). Search runs entirely on-device with zero network calls at query time.

| Metric | Score |
|--------|------:|
| Recall@3 | **97.8%** |
| Recall@5 | **100%** |
| MRR (mean reciprocal rank) | **89.5%** |

### Improvement Over Previous Strategy

The previous strategy embedded 3-5 formal descriptions per meeting (~6 vectors). The new strategy generates 8-15 conversational search phrases via Gemini, splits the summary into paragraphs, and embeds each action item individually (~28 vectors).

| Strategy | Vectors/meeting | R@3 | R@5 | MRR |
|----------|----------------:|----:|----:|----:|
| Old (formal descriptions) | 6 | 76.8% | 80.4% | 70.4% |
| **New (conversational phrases + paragraphs)** | **28** | **97.8%** | **100%** | **89.5%** |

The improvement is driven by two changes: conversational phrasing matches how users actually search, and paragraph-level embeddings preserve topic context that single-sentence splitting dilutes.

## Buried Sub-Topics in Long Meetings

The hardest test: finding specific details buried deep inside 90+ minute meetings with 6-10 distinct topics. 65 queries target details like specific numbers, person names, technical decisions, and niche sub-topics within marathon meetings.

| Strategy | Buried R@3 | Notes |
|----------|--------:|-------|
| Old (formal) | 61.5% | 3-5 descriptions can't cover 10 topics in a 2-hour meeting |
| **New (production)** | **98.5%** | Conversational phrases + paragraph embeddings cover sub-topics |

### Types of Buried Details Successfully Retrieved

| Detail type | Example query pattern | Result |
|-------------|----------------------|--------|
| Specific dollar amounts | Revenue figures, deal sizes, budget line items | Found in correct meeting |
| Person names in context | Named individuals and their specific contributions | Found in correct meeting |
| Technical decisions | Architecture choices, tool selections, migration plans | Found in correct meeting |
| Compliance/legal | Audit findings, regulatory requirements, SLA terms | Found in correct meeting |
| Competitive intelligence | Competitor evaluations, win/loss details | Found in correct meeting |
| HR/personnel | Hiring decisions, promotion candidates, on-call concerns | Found in correct meeting |
| Infrastructure specifics | Connection pool sizes, token counts, disk utilization | Found in correct meeting |

## Disambiguation

24 queries test whether the search picks the right meeting when the same topic is discussed across multiple meetings. For example, APAC expansion appears in the quarterly business review, the board meeting, and the sales kickoff — each with different details.

| Overlap topic | Meetings involved | R@3 |
|---------------|-------------------|----:|
| APAC expansion | Quarterly review, board meeting, sales kickoff | 100% |
| Pricing changes | Customer advisory board, pricing sync, customer demo | 100% |
| Audit logging | Advisory board, security review, product planning, sprint | 100% |
| Competitor evaluation | Advisory board, sales kickoff, quarterly review | 100% |
| Customer (GreenField Energy) | Advisory board, onboarding, quarterly review, pricing sync | 100% |
| Customer (DataStream Analytics) | CS QBR, quarterly review, incident post-mortem, weekly sync | 100% |
| SSO configuration | Advisory board, design review, product planning, onboarding | 100% |
| Microservices/auth service | Architecture review, product planning, sprint planning | 100% |
| Monitoring stack migration | Architecture review, infrastructure planning, budget review | 100% |

The system distinguishes between meetings using the specific context in each query — "board approved APAC budget" finds the board meeting, while "APAC territory assignment for new AEs" finds the sales kickoff.

## ASR Pipeline Artifacts

One meeting includes realistic noise from the speech-to-text pipeline: diarization errors (wrong speaker attribution), garbled jargon ("Rabbit MQ" for "RabbitMQ", "Terraforming" for "Terraform", "Elastic Search" for "Elasticsearch"), imprecise numbers, and thin sections from overlapping speech.

12 queries target this meeting — some using the correct terminology, some using the garbled version.

| Query style | R@1 | R@3 |
|-------------|----:|----:|
| Correct terms ("RabbitMQ", "Terraform") | 83% | 100% |
| ASR-garbled terms (matching the noisy summary) | 83% | 100% |

MiniLM's semantic matching handles the gap between correct and garbled terms — "RabbitMQ migration to Kubernetes" matches a summary containing "Rabbit MQ" because the surrounding context is strong enough.

## By Query Type

| Query type | Count | R@1 | R@3 |
|-----------|------:|----:|----:|
| Topic (direct match) | 11 | 90.9% | **100%** |
| Buried (sub-topic in long meeting) | 65 | 90.8% | **98.5%** |
| Disambiguation (right meeting among similar) | 24 | 75.0% | **100%** |
| Action item (specific task or owner) | 8 | 75.0% | **100%** |
| Decision (outcome queries) | 6 | 66.7% | **100%** |
| Person (participant or company) | 6 | 83.3% | **100%** |
| Conversational (casual phrasing) | 10 | 50.0% | **90%** |
| Vague (ambiguous, multiple valid matches) | 8 | 75.0% | **87.5%** |

Conversational queries ("that meeting where we talked about...") have the lowest R@3 because casual phrasing is semantically distant from both the specific search phrases and the formal summary text. These queries still find the correct meeting 90% of the time within the top 3.

## Known Failures

3 of 138 queries fail to rank the correct meeting in the top 3. All 3 find the correct meeting in the top 5 (R@5 = 100%).

**Casual phrasing vs multiple relevant meetings.** The query "when the CTO showed the long-term technical vision" expects the engineering all-hands but matches the board meeting (which also features the CTO discussing strategy). Both meetings are legitimate matches — the board meeting scores higher because its summary has denser CTO-related content.

**Vague query with broad relevance.** The query "customer churn risk" matches the sales kickoff (which discusses churn prevention) rather than the quarterly review or CS QBR (which discuss specific at-risk accounts). The term "churn risk" as a general concept matches many meetings that discuss customer retention.

**Frontend performance detail in a 150-minute business review.** A query about Lighthouse scores and code splitting targets a 2-sentence mention buried in a paragraph about engineering delivery within an 834-word quarterly review. The Gemini-generated search phrases and paragraph embeddings didn't capture this specific frontend performance detail. The correct meeting ranks 4th.

## How It Works

1. **Search phrase generation** (summarization time): Gemini 3 Flash generates 8-15 conversational search phrases per meeting alongside the summary. Phrases are written in speech-style phrasing with lowercase proper nouns, covering buried sub-topics and specific details — not just the main theme.

2. **Embedding** (summarization time, <300ms total): Title, full summary, each summary paragraph, each search phrase, and each action item are embedded individually on-device using all-MiniLM-L6-v2 (384-dim transformer). ~28 vectors per meeting.

3. **Search** (query time): The query is embedded on-device. Cosine similarity is computed against all meeting vectors within a 6-month window using Accelerate/vDSP batch dot products. Results are aggregated per meeting by max similarity — a meeting's score is its single best-matching vector.

4. **Hybrid ranking**: Vector similarity (50% weight) is combined with full-text search rank (30%), recency (10%), and meeting length (10%) to produce final results. The benchmark tests vector similarity in isolation.

## Benchmark vs Production

**Search phrases are Gemini-generated, not hand-crafted.** The benchmark includes both hand-crafted baselines and Gemini Flash 3-generated phrases. The production results (97.8% R@3) use Gemini-generated phrases, matching exactly what ships.

**Meeting summaries are synthetic but realistic.** The corpus includes synthetic summaries at production-realistic lengths (780-1,127 words for marathon meetings). One meeting includes ASR pipeline artifacts — diarization errors, garbled jargon, imprecise numbers — matching real pipeline output.

**Paragraph splitting matches production code.** The benchmark splits summaries on double newlines with a 30-character minimum, matching `MeetingEmbeddingManager.generateAndStoreEmbeddings()`.

**Embedding model matches production.** The benchmark uses `sentence-transformers/all-MiniLM-L6-v2`, the same model weights as the on-device Swift implementation via `swift-embeddings`.

**Search phrase generation is non-deterministic.** Gemini produces slightly different phrases on each run. The benchmark caches phrases to disk for reproducibility, but results may vary by 1-2% on fresh runs.
