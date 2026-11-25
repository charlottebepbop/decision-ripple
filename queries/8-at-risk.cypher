// Live decisions that rest on any of $assumptions.
// Critical rests sort before supporting. Confidence is not a filter:
// a high-confidence decision on a broken assumption is still at risk.
// Superseded decisions are absent (status is live).
MATCH (a:Assumption)<-[r:RESTS_ON]-(d:Decision {status: 'live'})
WHERE a.name IN $assumptions
OPTIONAL MATCH (d)-[:STEERS]->(p:Project)
RETURN a.name AS assumption, a.statement AS statement,
       d.title AS decision, d.confidence AS confidence,
       coalesce(r.weight, 'supporting') AS weight,
       collect(DISTINCT p.title) AS projects
ORDER BY assumption, weight, decision;
