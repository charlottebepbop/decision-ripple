---
type: Decision
confidence: medium
date: 2026-09-30
name: 2026-09-30-ops-dashboard-on-scan-data
status: live
title: Build the ops dashboard on scan data
DECIDED_BY:
  - "[[Person/lea-novak]]"
RESTS_ON:
  - target: "[[Assumption/ops-data-complete]]"
    weight: critical
STEERS:
  - "[[Project/ops-dashboard]]"
---

# Build the ops dashboard on scan data

**Rationale:** Scans are the only per-trip record we have.
