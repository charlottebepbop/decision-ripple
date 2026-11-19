---
type: Decision
confidence: low
date: 2026-10-21
name: 2026-10-21-optimizer-uses-scan-data-only
status: live
title: The optimizer trains on scan data only
DECIDED_BY:
  - "[[Person/ken-ito]]"
  - "[[Person/lea-novak]]"
RESTS_ON:
  - target: "[[Assumption/ops-data-complete]]"
    weight: critical
STEERS:
  - "[[Project/ops-dashboard]]"
  - "[[Project/route-optimizer-v2]]"
---

# The optimizer trains on scan data only

**Rationale:** GPS traces are too noisy in the old town.

## Context
Route optimizer v2 needs past trip times to learn from. GPS traces jump between streets in the old town, by up to 60 metres. Delivery scans give clean stop times instead.

## Options considered
- Train the optimizer on delivery scans only.
- Use GPS traces and clean them. Lost because cleaning failed on narrow streets.
- Mix GPS and scans. Lost because the two disagree on stop order.

## Who argued what
- Ken Ito (CTO) chose scans for model quality.
- Lea Novak (BizOps Lead) wants the dashboard and optimizer to share one data source.
- Diego Morales (Fleet Lead) noted riders sometimes forget the drop-off scan.

## What would change our mind
This depends on scans covering at least 95% of trips. If coverage falls below that, the model learns from a biased sample.
