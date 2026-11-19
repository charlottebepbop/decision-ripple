---
type: Decision
confidence: medium
date: 2026-09-09
name: 2026-09-09-mapping-api-annual-contract
status: superseded
title: Sign an annual mapping API contract
DECIDED_BY:
  - "[[Person/ken-ito]]"
  - "[[Person/priya-raman]]"
RESTS_ON:
  - "[[Assumption/route-api-pricing-stable]]"
STEERS:
  - "[[Project/route-optimizer-v2]]"
---

# Sign an annual mapping API contract

**Rationale:** 20% cheaper than monthly.

## Context
Route optimizer v2 calls the mapping API for distances and street data. We pay about EUR 2,400 a month on the monthly plan. The vendor offers an annual contract at 20% less.

## Options considered
- Sign the annual contract.
- Stay on the monthly plan. Lost because it costs about EUR 5,800 more a year.
- Switch to an open map source. Lost because it lacks loading zone data.

## Who argued what
- Ken Ito (CTO) wants a stable price while the optimizer is built.
- Priya Raman (Head of Finance) supports the discount.
- Diego Morales (Fleet Lead) asked that the contract cover traffic updates.

## What would change our mind
If the vendor raises prices for 2027 anyway, the annual lock-in loses value. We would compare other vendors at renewal.
