// Agent pre-check: before touching a project, which decisions bind it,
// which live decision replaced the old ones, which live decision amended
// them and what that amendment rests on, and which assumptions underneath
// are under pressure?
// SUPERSEDES and AMENDS are walked up to five hops. Only a decision that
// is still live is named. An amendment does not replace the decision it changes.
MATCH (p:Project {name: $project})<-[:STEERS]-(d:Decision)
OPTIONAL MATCH (newer:Decision {status: 'live'})-[:SUPERSEDES*1..5]->(d)
OPTIONAL MATCH (amendment:Decision {status: 'live'})-[:AMENDS*1..5]->(d)
OPTIONAL MATCH (amendment)-[g:RESTS_ON]->(ground:Assumption)
OPTIONAL MATCH (d)-[:RESTS_ON]->(a:Assumption)<-[hit:WEAKENS|BREAKS]-(s:Signal)
RETURN d.title AS decision, d.status AS status,
       [t IN collect(DISTINCT newer.title) WHERE t IS NOT NULL] AS replaced_by,
       [t IN collect(DISTINCT amendment.title) WHERE t IS NOT NULL] AS amended_by,
       [t IN collect(DISTINCT amendment.title + ': ' + ground.name + ' (' + coalesce(g.weight, 'supporting') + ')') WHERE t IS NOT NULL] AS amendment_rests_on,
       collect(DISTINCT a.name + ': ' + s.title) AS pressure
ORDER BY status, decision;
