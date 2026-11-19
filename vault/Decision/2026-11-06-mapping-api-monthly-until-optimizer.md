---
type: Decision
confidence: low
date: 2026-11-06
name: 2026-11-06-mapping-api-monthly-until-optimizer
status: live
title: Pay the mapping API monthly until the optimizer ships
DECIDED_BY:
  - "[[Person/ken-ito]]"
RESTS_ON:
  - target: "[[Assumption/route-api-pricing-stable]]"
    weight: critical
STEERS:
  - "[[Project/route-optimizer-v2]]"
SUPERSEDES:
  - "[[Decision/2026-09-09-mapping-api-annual-contract]]"
---

# Pay the mapping API monthly until the optimizer ships

**Rationale:** We may not need it after v2.
