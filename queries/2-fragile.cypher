// Fragile ground. A project is listed when either:
// - 2 or more low-confidence live decisions steer it, or
// - a high-confidence live decision that steers it rests on an assumption
//   a signal has broken (a BREAKS edge, not a weaken).
// Those high-confidence decisions are counted on their own. They are the
// ones that were made as if the ground would hold.
// hit_assumptions are assumptions under the counted decisions that a signal
// has weakened or broken.
MATCH (p:Project)
OPTIONAL MATCH (p)<-[:STEERS]-(low:Decision {status: 'live', confidence: 'low'})
WITH p, [d IN collect(DISTINCT low) WHERE d IS NOT NULL] AS weak
OPTIONAL MATCH (p)<-[:STEERS]-(high:Decision {status: 'live', confidence: 'high'})-[:RESTS_ON]->(:Assumption)<-[:BREAKS]-(:Signal)
WITH p, weak, [d IN collect(DISTINCT high) WHERE d IS NOT NULL] AS confident_broken
WHERE size(weak) >= 2 OR size(confident_broken) >= 1
WITH p, size(weak) AS low_n, size(confident_broken) AS high_n,
     weak + confident_broken AS counted
UNWIND counted AS d
OPTIONAL MATCH (d)-[:RESTS_ON]->(a:Assumption)<-[hit:WEAKENS|BREAKS]-(:Signal)
RETURN p.name AS project,
       low_n AS low_confidence_decisions,
       high_n AS high_confidence_broken,
       collect(DISTINCT d.title) AS decisions,
       [t IN collect(DISTINCT a.name + ' (' + type(hit) + ')') WHERE t IS NOT NULL] AS hit_assumptions
ORDER BY high_confidence_broken DESC, low_confidence_decisions DESC, project;
