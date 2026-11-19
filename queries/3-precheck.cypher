// Agent pre-check: before touching a project, which decisions bind it,
// which live decision replaced the old ones, and which assumptions underneath are under pressure?
MATCH (p:Project {name: $project})<-[:STEERS]-(d:Decision)
OPTIONAL MATCH (newer:Decision {status: 'live'})-[:SUPERSEDES*1..5]->(d)
OPTIONAL MATCH (d)-[:RESTS_ON]->(a:Assumption)<-[hit:WEAKENS|BREAKS]-(s:Signal)
RETURN d.title AS decision, d.status AS status,
       [t IN collect(DISTINCT newer.title) WHERE t IS NOT NULL] AS replaced_by,
       collect(DISTINCT a.name + ': ' + s.title) AS pressure
ORDER BY status, decision;
