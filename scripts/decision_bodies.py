"""Longer markdown bodies for the sample decisions in seed_vault.py.

Each body replaces the short title-plus-rationale body. Keys match DECISIONS slugs.
All people, places and numbers are invented for the Kestrel Cargo demo.
"""

BODIES = {
    "2026-06-05-driver-bonus-for-retention": """# Pay a 3-month retention bonus to drivers

**Rationale:** Replacing a driver costs more than the bonus.

## Context
Three drivers quit in May, all within their first quarter. Each new driver needs about two weeks of paid ride-alongs before working solo. The bonus is EUR 300, paid after 3 months of service.

## Options considered
- A flat EUR 300 retention bonus at the 3-month mark.
- A higher hourly wage for everyone. Lost because it costs more and rewards drivers who would stay anyway.

## Who argued what
- Saskia de Wit (People Lead) proposed the bonus and owns the payout.
- Priya Raman (Head of Finance) asked for a cap so the cost stays below one onboarding.

## What would change our mind
If monthly driver churn rises above 8% even with the bonus, it is not working. Then we look at pay or shift patterns instead.
""",

    "2026-06-12-launch-lyon-before-paris": """# Launch Lyon before Paris

**Rationale:** Lyon is smaller, and its permit process is faster.

## Context
We want a second country by spring. Paris has more demand, but its depot permit queue runs over 9 months. Lyon's city office quoted about 6 months for a cargo-bike depot.

## Options considered
- Launch Lyon first, Paris later.
- Launch Paris first. Lost because the permit wait would push launch past the Series A.
- Launch both at once. Lost because we cannot staff two new cities with one launch team.

## Who argued what
- Hanna Berg (Head of Growth) pushed for Lyon as a smaller test market.
- Ines Varga (CEO) agreed, if Lyon is live before the Series A closes.

## What would change our mind
If Lyon does not grant the depot permit by 15 Jan, the speed advantage is gone. A slip in the Series A would also make a second city harder to fund.
""",

    "2026-06-20-buy-ebikes-not-lease": """# Buy the e-cargo bikes outright

**Rationale:** Buying is cheaper over 3 years with the subsidy.

## Context
We are replacing 60 bikes with e-cargo bikes. Leasing costs about EUR 95 per bike a month. Buying costs about EUR 4,100 per bike before any subsidy. Over 3 years, buying wins if the Dutch subsidy renews.

## Options considered
- Buy all 60 e-cargo bikes outright.
- Lease all 60. Lost because the 3-year total is higher.
- Keep the old bikes one more year. Lost because repair costs doubled this spring.

## Who argued what
- Priya Raman (Head of Finance) ran the 3-year cost model and favours buying.
- Diego Morales (Fleet Lead) prefers owning so his team controls repairs.
- Tomasz Wilk (COO) asked that the purchase fit inside the Q1 budget.

## What would change our mind
If the Q1 budget drops below the EUR 2.4m plan, a large upfront purchase no longer fits. If the subsidy does not renew, buying loses its cost edge.
""",

    "2026-06-30-paris-waits-for-lyon-data": """# Paris waits for 3 months of Lyon data

**Rationale:** We want unit economics from one French city first.

## Context
After choosing Lyon first, the board asked when Paris follows. We do not know French cost per delivery yet. Labour rules and parcel density differ from Rotterdam.

## Options considered
- Start Paris planning only after 3 full months of Lyon numbers.
- Start Paris planning in parallel. Lost because we would guess at cost per delivery.
- Drop Paris from the plan. Lost because it is still the largest market.

## Who argued what
- Ines Varga (CEO) set the 3-month rule.
- Priya Raman (Head of Finance) wants cost per delivery and driver cost per hour from Lyon.
- Olu Adeyemi (Head of Operations) asked that winter months not count as a full sample.

## What would change our mind
If the Lyon permit is late, the 3-month clock starts late too. Paris would then slip with it, and we would revisit the rule.
""",

    "2026-07-03-lyon-depot-in-guillotiere": """# Put the Lyon depot in Guillotiere

**Rationale:** Shortest average route to the customers we have signed.

## Context
We have letters of intent from 7 Lyon shops and restaurants. Most sit east of the Rhone. A depot in Guillotiere gives an average route of 2.8 km to them.

## Options considered
- A ground-floor depot in Guillotiere.
- A unit in Part-Dieu. Lost because rent was about 40% higher.
- A site near Gerland. Lost because routes cross the river twice.

## Who argued what
- Olu Adeyemi (Head of Operations) chose Guillotiere on route length.
- Priya Raman (Head of Finance) checked the rent against the launch budget.
- Ines Varga (CEO) asked for a lease we can exit within 12 months.

## What would change our mind
The depot needs the cargo-bike permit by 15 Jan. If the permit office rejects this address, we move to the next site on the list.
""",

    "2026-07-08-apply-for-ebike-subsidy": """# Apply for the Dutch e-cargo-bike subsidy

**Rationale:** Covers 30% of the purchase price.

## Context
The fleet upgrade replaces 60 bikes with e-cargo bikes. The Dutch subsidy pays 30% of the purchase price per bike. The application window closes in September, and payout follows delivery.

## Options considered
- Apply now for all 60 bikes.
- Wait until the bikes arrive. Lost because the window may close first.
- Skip the subsidy. Lost because it is the main reason buying beats leasing.

## Who argued what
- Priya Raman (Head of Finance) owns the application and the paperwork.
- Tomasz Wilk (COO) asked that we still plan the fleet as if no subsidy came, as a fallback.

## What would change our mind
If the government does not renew the subsidy for 2027, the application is moot. We would then redo the buy versus lease numbers without it.
""",

    "2026-07-15-cs-stays-at-five": """# Customer Success stays at 5 people

**Rationale:** Ticket volume per customer is falling.

## Context
Customer count grew 18% this half. Tickets per customer fell from 2.1 to 1.4 a month after the tracking page went live. The team of 5 clears the queue within one working day.

## Options considered
- Keep Customer Success at 5 people.
- Hire a sixth person for enterprise accounts. Lost because enterprise deals are not signed yet.
- Cut to 4. Lost because the SLA program will add reporting work.

## Who argued what
- Ruth Mensah (Customer Success Lead) said 5 is enough if enterprise stays small.
- Tomasz Wilk (COO) wanted headcount flat until the Series A.
- Hanna Berg (Head of Growth) warned enterprise pilots need more hand-holding.

## What would change our mind
If 3 or more enterprise pilots convert, each needs a named contact. Then 5 people is not enough and we hire.
""",

    "2026-07-29-open-south-hub-q1": """# Open the Rotterdam South hub in Q1

**Rationale:** The north hub runs at 92% capacity.

## Context
The north hub runs at 92% capacity. Bikes queue at the loading dock from 7:00 to 8:30. Half of new customers sit south of the Maas.

## Options considered
- Open a second hub in Rotterdam South in Q1.
- Extend north hub hours into a night shift. Lost because neighbours already complain about noise.
- Rent a small overflow unit near the north hub. Lost because it does not shorten southern routes.

## Who argued what
- Olu Adeyemi (Head of Operations) owns the hub and pushed for Q1.
- Tomasz Wilk (COO) agreed if the lease is signed by December.
- Priya Raman (Head of Finance) asked that fit-out stay inside the EUR 2.4m Q1 budget.

## What would change our mind
No signed lease by December means no Q1 opening. A Q1 budget cut would also delay it.
""",

    "2026-08-01-runway-plan-assumes-march-close": """# Runway plan assumes the Series A closes in March

**Rationale:** Lead investor gave a verbal term sheet.

## Context
We have 14 months of runway at current burn. The south hub and the Lyon launch both start spending in Q1. The lead investor gave a verbal term sheet in July, with closing expected in March.

## Options considered
- Plan spend on a March close.
- Plan on a June close. Lost because it would delay both the south hub and Lyon by a quarter.

## Who argued what
- Ines Varga (CEO) said the verbal term sheet is firm enough to plan on.
- Priya Raman (Head of Finance) wants a monthly check on the close date.
- Tomasz Wilk (COO) asked which hub costs can be paused if it slips.

## What would change our mind
If the Series A will not close by end of March, the runway plan breaks. Hub and Lyon spend would need to pause.
""",

    "2026-08-11-build-route-optimizer-in-house": """# Build the route optimizer in house

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
""",

    "2026-08-25-enterprise-tier-at-1800": """# Price the enterprise tier at EUR 1,800 a month

**Rationale:** Three prospects named a budget between 1,500 and 2,000.

## Context
Larger shippers want a fixed monthly price instead of per-parcel billing. Three prospects named budgets between EUR 1,500 and 2,000 a month. Our cost to serve one is about EUR 1,100.

## Options considered
- A flat EUR 1,800 a month, with a parcel allowance.
- EUR 1,500 to win faster. Lost because the margin is too thin.
- Keep per-parcel pricing. Lost because procurement teams asked for a fixed budget.

## Who argued what
- Hanna Berg (Head of Growth) picked 1,800 as the top of the range that still closes.
- Priya Raman (Head of Finance) checked the margin per account.
- Ruth Mensah (Customer Success Lead) asked what support level the price includes.

## What would change our mind
If fewer than 3 pilot customers convert by end of Q1, the price is wrong or the tier is. We would then test a lower price.
""",

    "2026-09-02-staff-south-hub-from-north": """# Staff the south hub with drivers from the north hub

**Rationale:** Experienced drivers lower the error rate in a new hub.

## Context
New drivers make about 3 times more delivery errors in their first month. A new hub with only new drivers would start with a high error rate. We plan to move 12 experienced drivers south and backfill the north hub.

## Options considered
- Move experienced north hub drivers south, and hire new drivers for the north.
- Staff the south hub with new hires only. Lost because errors would land on new customers.

## Who argued what
- Olu Adeyemi (Head of Operations) wants the transfer.
- Saskia de Wit (People Lead) owns the backfill hiring.
- Tomasz Wilk (COO) asked that no driver moves without agreeing to it.

## What would change our mind
This needs driver churn under 8% and 40 qualified applicants a month. Otherwise the backfill fails.
""",

    "2026-09-09-mapping-api-annual-contract": """# Sign an annual mapping API contract

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
""",

    "2026-09-18-hire-lyon-city-lead-in-dec": """# Hire the Lyon city lead in December

**Rationale:** The lead needs 6 weeks before the first driver starts.

## Context
Lyon drivers start in late January if the depot permit arrives on time. The city lead must set up the depot, local payroll and the first driver hires. That takes about 6 weeks.

## Options considered
- Hire the city lead to start in December.
- Hire in January with the drivers. Lost because no one would prepare the depot.

## Who argued what
- Hanna Berg (Head of Growth) owns the Lyon launch and wants the lead early.
- Saskia de Wit (People Lead) runs the search with a French recruiter.
- Priya Raman (Head of Finance) asked that December salary come out of the Q1 plan.

## What would change our mind
If the Q1 budget is cut, a December hire is the first thing to delay. If the Lyon permit slips past 15 Jan, the start date moves too.
""",

    "2026-09-30-ops-dashboard-on-scan-data": """# Build the ops dashboard on scan data

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
""",

    "2026-10-02-lease-half-buy-half": """# Lease half the e-cargo bikes, buy half

**Rationale:** Keeps cash for the south hub.

## Context
This replaces "Buy the e-cargo bikes outright". Buying all 60 would take most of the fleet budget in one quarter. The south hub fit-out lands in the same quarter.

## Options considered
- Lease 30 e-cargo bikes and buy 30.
- Keep the plan to buy all 60. Lost because it leaves too little cash for the south hub.
- Lease all 60. Lost because the 30% subsidy only applies to bikes we buy.

## Who argued what
- Priya Raman (Head of Finance) proposed the split to protect cash.
- Diego Morales (Fleet Lead) wants the owned bikes on the longest routes.
- Tomasz Wilk (COO) signed off on timing with the south hub.

## What would change our mind
The supplier must deliver all 60 bikes by end of February. A late delivery, a Q1 budget cut or no subsidy renewal would reopen the split.
""",

    "2026-10-07-winter-shift-plan-two-waves": """# Run winter shifts in two waves

**Rationale:** Matches the morning and afternoon parcel peaks.

## Context
Winter parcel volume peaks twice a day, at 8:00 and at 14:00. Midday has about 40% fewer stops. A single long shift leaves riders idle at noon.

## Options considered
- Two shift waves, morning and afternoon.
- One long day shift. Lost because idle hours cost money and riders get cold.
- A night shift for next-day parcels. Lost because customers do not accept night drop-offs.

## Who argued what
- Olu Adeyemi (Head of Operations) designed the two waves.
- Priya Raman (Head of Finance) checked that split shifts do not raise hourly cost.
- Hanna Berg (Head of Growth) asked that SLA delivery windows match the waves.

## What would change our mind
The plan assumes winter volume drops by at most 15%. A deeper drop would make one wave enough.
""",

    "2026-10-14-hire-25-drivers-q1": """# Hire 25 drivers in Q1

**Rationale:** Covers the south hub and Lyon.

## Context
The south hub needs backfill after experienced drivers move from the north. Lyon needs its first drivers once the depot opens. Together that is 25 new drivers in Q1.

## Options considered
- Hire 25 drivers across January to March.
- Hire 15 and use agency riders for the rest. Lost because agency riders do not know our routes.
- Hire all 25 in January. Lost because trainers can onboard about 10 a month.

## Who argued what
- Saskia de Wit (People Lead) owns the hiring plan.
- Olu Adeyemi (Head of Operations) split the 25 between Rotterdam and Lyon.
- Priya Raman (Head of Finance) asked that it fit the EUR 2.4m Q1 budget.

## What would change our mind
We need 40 qualified applicants a month to hit 25. A Q1 budget cut or a weak pipeline cuts the number. A deep winter dip would let us hire later.
""",

    "2026-10-21-optimizer-uses-scan-data-only": """# The optimizer trains on scan data only

**Rationale:** GPS traces are too noisy in the old town.

## Context
Route optimizer v2 needs past trip times to learn from. GPS traces jump between streets in the old town, by up to 60 metres. Delivery scans give clean stop times instead.

## Options considered
- Train the optimizer on delivery scans only.
- Use GPS traces and clean them. Lost because cleaning failed on narrow streets.
- Mix GPS and scans. Lost because the two disagree on stop order.

## Who argued what
- Ken Ito (CTO) chose scans for model quality.
- Lea Novak (BizOps Lead) wants the dashboard and optimizer to share one data source.
- Diego Morales (Fleet Lead) noted riders sometimes forget the drop-off scan.

## What would change our mind
This depends on scans covering at least 95% of trips. If coverage falls below that, the model learns from a biased sample.
""",

    "2026-10-28-sla-98-percent-on-time": """# Promise 98% on-time delivery in the SLA

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
""",

    "2026-11-04-enterprise-tier-adds-sla": """# The enterprise tier includes the SLA

**Rationale:** Two of three pilots made the SLA a condition.

## Context
This amends "Price the enterprise tier at EUR 1,800 a month". The price stays. The 98% on-time SLA is now part of the tier, not an add-on.

## Options considered
- Include the SLA in the EUR 1,800 tier.
- Sell the SLA as a paid add-on. Lost because two pilot customers would walk.
- Raise the price to cover SLA risk. Lost because it exceeds the named budgets.

## Who argued what
- Hanna Berg (Head of Growth) wants the SLA bundled to close the pilots.
- Ruth Mensah (Customer Success Lead) will report SLA results to each account.
- Priya Raman (Head of Finance) asked for the penalty cap in every contract.

## What would change our mind
If penalties are not capped at 5% of contract value, bundling is too risky. If fewer than 3 pilots convert, we revisit the whole tier.
""",

    "2026-11-06-mapping-api-monthly-until-optimizer": """# Pay the mapping API monthly until the optimizer ships

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
""",

    "2026-11-10-weekly-ops-review-from-dashboard": """# Run the weekly ops review from the dashboard

**Rationale:** One set of numbers in the room.

## Context
The Monday ops review spends its first 20 minutes arguing about whose numbers are right. Each hub lead brings a different spreadsheet. The ops dashboard now shows on-time rate and stops per hub.

## Options considered
- Run the review from the ops dashboard only.
- Keep hub spreadsheets alongside it. Lost because the arguments would continue.
- Wait for a finished dashboard. Lost because the review needs fixing now.

## Who argued what
- Tomasz Wilk (COO) chairs the review and wants one source.
- Lea Novak (BizOps Lead) will fix any gaps the review finds.
- Olu Adeyemi (Head of Operations) asked for a per-hub view on page one.

## What would change our mind
The dashboard is built on delivery scans. If scan coverage drops well below 95%, the room will stop trusting it.
""",

    "2026-11-12-freeze-hires-outside-ops": """# Freeze hiring outside Operations until the Series A closes

**Rationale:** Protects runway if the round slips.

## Context
The runway plan assumes the Series A closes in March. If it slips, every new salary shortens runway. Operations hires keep going, because the south hub and Lyon need drivers. The freeze pauses a sixth Customer Success hire and an enterprise sales role.

## Options considered
- Freeze all hiring outside Operations until the round closes.
- Freeze all hiring, drivers included. Lost because it would stall the south hub.
- No freeze. Lost because it leaves no buffer if the close slips.

## Who argued what
- Ines Varga (CEO) made the call.
- Priya Raman (Head of Finance) will lift the freeze the week the round closes.
- Olu Adeyemi (Head of Operations) confirmed driver hiring stays exempt.

## What would change our mind
If the Series A closes by end of March, the freeze ends. A cut to the EUR 2.4m Q1 budget could widen it.
""",
}
