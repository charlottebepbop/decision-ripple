// Ripple: an assumption breaks. Which live decisions rest on it,
// which projects do they steer, and who has to hear about it?
MATCH (a:Assumption {name: $assumption})<-[r:RESTS_ON]-(d:Decision {status: 'live'})
MATCH (d)-[:STEERS]->(p:Project)
OPTIONAL MATCH (who:Person)
  WHERE (p)-[:OWNED_BY|STAKEHOLDER]->(who) OR (d)-[:DECIDED_BY]->(who)
RETURN d.title AS decision,
       coalesce(r.weight, 'supporting') AS weight,
       d.confidence AS confidence,
       collect(DISTINCT p.name) AS projects,
       collect(DISTINCT who.title) AS tell
ORDER BY weight, decision;
