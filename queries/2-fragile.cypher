// Fragile ground: projects steered by 2 or more low-confidence live decisions,
// plus any assumption under them that a signal has already weakened or broken.
MATCH (p:Project)<-[:STEERS]-(d:Decision {status: 'live', confidence: 'low'})
WITH p, collect(d) AS weak
WHERE size(weak) >= 2
UNWIND weak AS d
OPTIONAL MATCH (d)-[:RESTS_ON]->(a:Assumption)<-[hit:WEAKENS|BREAKS]-(:Signal)
RETURN p.name AS project, size(weak) AS low_confidence_decisions,
       collect(DISTINCT d.title) AS decisions,
       collect(DISTINCT a.name + ' (' + type(hit) + ')') AS hit_assumptions
ORDER BY low_confidence_decisions DESC;
