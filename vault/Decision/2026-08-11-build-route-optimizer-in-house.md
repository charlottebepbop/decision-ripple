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

## Context
We tested two vendor route planners on 500 past trips. Both sent bikes down car-only streets and ignored loading zones. Riders rerouted by hand on 1 in 5 stops.

## Options considered
- Build route optimizer v2 in house on top of the mapping API.
- Buy a vendor planner and patch it. Lost because the bike lane gaps are in their core model.

## Who argued what
- Ken Ito (CTO) wants to own the model and the bike lane rules.
- Diego Morales (Fleet Lead) asked for loading zones and bike weight limits in v1.
- Olu Adeyemi (Head of Operations) wants it live before the south hub opens.

## What would change our mind
The build relies on the mapping API price staying flat, and on delivery scans covering 95% of trips. If either fails, buying looks better.
