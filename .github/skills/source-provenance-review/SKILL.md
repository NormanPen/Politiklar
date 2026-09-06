---
name: source-provenance-review
description: 'Review crawler, ingestion, transformation, search, and political-data changes for source provenance, traceability, reproducibility, neutrality, and evidence-backed output.'
argument-hint: 'Describe the data flow or files to review.'
---

# Source Provenance Review

## When to use

- Reviewing crawler or ingestion changes
- Adding a political data source or parser
- Reviewing transformations, search results, summaries, or citations
- Checking whether an AI response is grounded in retrieved evidence

## Procedure

1. Identify the source boundary and follow the data from retrieval through storage, transformation, retrieval, and presentation.
2. Check that the implementation preserves the original source URL, source identity, publication or document date, and retrieval timestamp whenever those values are available.
3. Check that parsing and transformation steps are deterministic, observable, and safe to repeat without duplicating records.
4. Check malformed, unavailable, changed, and contradictory source content. The system should fail explicitly or mark uncertainty rather than silently fabricating values.
5. Check that summaries and search answers distinguish quoted source facts from generated interpretation and link claims to the evidence used.
6. Check for neutral wording and flag unsupported political judgments, rankings, intent attribution, or conclusions that are not present in the source.
7. Require focused tests or fixtures covering provenance fields, duplicate handling, changed source content, and insufficient evidence.
8. Report findings with the affected file, the missing guarantee, and a concrete correction. Do not treat a passing parser test as proof that end-to-end traceability exists.

## Review output

Order findings by severity. Separate correctness or traceability defects from follow-up improvements, and state which checks were actually run.