---
type: Decision
confidence: low
date: 2026-10-28
name: 2026-10-28-sla-98-percent-on-time
status: live
title: Promise 98% on-time delivery in the SLA
DECIDED_BY:
  - "[[Person/olu-adeyemi]]"
  - "[[Person/ruth-mensah]]"
RESTS_ON:
  - target: "[[Assumption/driver-churn-under-8]]"
    weight: critical
  - target: "[[Assumption/sla-penalties-capped]]"
    weight: critical
  - "[[Assumption/winter-volume-dip-15]]"
STEERS:
  - "[[Project/customer-sla-program]]"
---

# Promise 98% on-time delivery in the SLA

**Rationale:** Enterprise prospects asked for a number above 97%.
