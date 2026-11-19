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
