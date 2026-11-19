// What is already broken: a signal weakens or breaks an assumption,
// and a live decision still rests on it.
MATCH (s:Signal)-[hit:BREAKS|WEAKENS]->(a:Assumption)<-[r:RESTS_ON]-(d:Decision {status: 'live'})
OPTIONAL MATCH (d)-[:STEERS]->(p:Project)
RETURN s.title AS signal, type(hit) AS effect, a.name AS assumption,
       d.title AS decision,
       coalesce(r.weight, 'supporting') AS weight,
       collect(DISTINCT p.name) AS projects
ORDER BY effect, weight, decision;
