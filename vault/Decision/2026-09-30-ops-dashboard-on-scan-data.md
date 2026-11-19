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

## Context
Ops leads track deliveries in three spreadsheets that never match. Every parcel is scanned at pickup and at drop-off. Those scans hold a trip ID, time and rider for each stop.

## Options considered
- Build the dashboard on delivery scans.
- Build it on rider shift sheets. Lost because they are filled in by hand at the end of the day.
- Use customer complaints as the main signal. Lost because they only show failures.

## Who argued what
- Lea Novak (BizOps Lead) owns the dashboard and chose scans.
- Olu Adeyemi (Head of Operations) wants on-time rate per hub.
- Tomasz Wilk (COO) asked for one number per hub per day.

## What would change our mind
The dashboard is only right if scans cover at least 95% of trips. Missed scans would make on-time rates look worse or better than they are.
