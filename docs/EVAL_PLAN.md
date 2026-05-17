# Evaluation Plan

## RAG Evaluation

- Retrieval hit rate on known SOP/manual questions.
- Citation presence for every answer.
- Source chunk relevance checks.
- Lightweight faithfulness checks against retrieved context.

## LLMOps Evaluation

- Structured output schema validity.
- Recommendation completeness.
- Fallback behavior when the primary provider fails.
- Latency and error-rate tracking by model/provider.

## ML Evaluation

- Train/test split metrics for AI4I-style predictive maintenance.
- Classification metrics including precision, recall, F1, and confusion matrix.
- Feature importance or explainability report where practical.
- Stored model artifact metadata through MLflow.

## Security Evaluation

- Secret scan passes.
- Dependency/container vulnerability scan has no critical unresolved findings.
- RLS policy tests verify role separation.
- Backend tests verify client code cannot access server-only settings.

## Demo Acceptance

The demo is considered ready when the main scenario returns cited recommendations, valid structured JSON, a risk score, a reviewable work order, and visible security/observability proof.
