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

## Context
Enterprise prospects want a written on-time promise. Our on-time rate was 98.4% in September at the north hub. The penalty clause pays credits when we miss.

## Options considered
- Promise 98% on-time, measured monthly.
- Promise 97%. Lost because prospects said it was too low.
- Promise 99%. Lost because one bad week would break it.

## Who argued what
- Ruth Mensah (Customer Success Lead) owns the SLA and proposed 98%.
- Olu Adeyemi (Head of Operations) accepted it if winter shifts hold.
- Hanna Berg (Head of Growth) said 98% is the number that closes deals.

## What would change our mind
This needs driver churn under 8% and penalties capped at 5% of contract value. If either fails, the risk is too high. A winter volume dip over 15% would also strain it.
