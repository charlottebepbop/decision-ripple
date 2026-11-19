---
type: Decision
confidence: low
date: 2026-08-11
name: 2026-08-11-build-route-optimizer-in-house
status: live
title: Build the route optimizer in house
DECIDED_BY:
  - "[[Person/ken-ito]]"
RESTS_ON:
  - target: "[[Assumption/ops-data-complete]]"
    weight: critical
  - target: "[[Assumption/route-api-pricing-stable]]"
    weight: critical
STEERS:
  - "[[Project/route-optimizer-v2]]"
---

# Build the route optimizer in house

**Rationale:** Vendor tools do not handle bike lanes and loading zones.
