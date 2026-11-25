// What a signal has done to an assumption a live decision still rests on.
// BREAKS and WEAKENS are risk. SUPPORTS is support (evidence, not proof).
// CONFIRMS is confirmation. The label is there so good news is not read as risk.
// Risk rows come first. There is no date window.
MATCH (s:Signal)-[hit:BREAKS|WEAKENS|SUPPORTS|CONFIRMS]->(a:Assumption)<-[r:RESTS_ON]-(d:Decision {status: 'live'})
OPTIONAL MATCH (d)-[:STEERS]->(p:Project)
RETURN s.title AS signal, type(hit) AS effect,
       CASE type(hit)
         WHEN 'SUPPORTS' THEN 'support'
         WHEN 'CONFIRMS' THEN 'confirmation'
         ELSE 'risk'
       END AS label,
       a.name AS assumption,
       d.title AS decision,
       coalesce(r.weight, 'supporting') AS weight,
       collect(DISTINCT p.name) AS projects
ORDER BY CASE effect
           WHEN 'BREAKS' THEN 0
           WHEN 'WEAKENS' THEN 1
           WHEN 'CONFIRMS' THEN 2
           ELSE 3
         END,
         weight, decision;
