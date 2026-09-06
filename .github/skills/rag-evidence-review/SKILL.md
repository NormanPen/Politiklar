---
name: rag-evidence-review
description: 'Review native RAG retrieval, chunking, embeddings, ranking, citations, and generated answers for evidence grounding, reproducibility, and hallucination resistance.'
argument-hint: 'Describe the RAG flow, evaluation case, or files to review.'
---

# RAG Evidence Review

## When to use

- Designing or reviewing a retrieval pipeline
- Changing chunking, embeddings, vector search, or ranking
- Reviewing citations and answer-generation logic
- Adding a regression or evaluation case for grounded answers

## Procedure

1. Map the pipeline: document selection, chunking, metadata, embedding, retrieval, ranking, context assembly, generation, and citation rendering.
2. Verify that each retrieved chunk retains stable document identity and source-location metadata so a user can inspect the evidence.
3. Check that chunking does not discard headings, dates, speaker identity, document boundaries, or other context needed to interpret political text.
4. Check that retrieval and answer generation have an explicit insufficient-evidence path. The model must be able to decline to answer instead of filling gaps.
5. Check that prompts and output schemas distinguish evidence from conclusions and require citations for factual claims.
6. Check deterministic fixtures for exact source attribution, relevant retrieval, irrelevant-query behavior, and contradictory or incomplete evidence.
7. Check that embedding-model changes record compatibility information and trigger a deliberate reindex or migration plan.
8. Report unsupported claims, citation mismatches, retrieval regressions, and missing evaluation coverage before stylistic improvements.

## Constraints

- Do not assume a framework-specific API or evaluation library unless it exists in the repository.
- Prefer a small, repeatable evaluation set over subjective inspection of a single generated answer.
- Treat citation presence alone as insufficient; citations must support the claim they are attached to.