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

## Context
This supersedes "Sign an annual mapping API contract". Route optimizer v2 may use its own street data for most routing. A 12-month commitment could leave us paying for unused calls.

## Options considered
- Stay on the monthly plan until optimizer v2 ships.
- Keep the annual contract plan. Lost because we may not need the API after v2.
- Cut API use now. Lost because current routing still depends on it.

## Who argued what
- Ken Ito (CTO) made the call to stay flexible.
- Olu Adeyemi (Head of Operations) asked that routing quality not drop in the meantime.
- Diego Morales (Fleet Lead) wants traffic updates kept until v2 is live.

## What would change our mind
Monthly only works if the price stays flat. If the vendor raises monthly prices, an annual deal looks better again.
