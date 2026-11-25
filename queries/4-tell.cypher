// Who to tell: the ripple from 1-ripple.cypher, turned around per person.
MATCH (a:Assumption {name: $assumption})<-[r:RESTS_ON]-(d:Decision {status: 'live'})
MATCH (d)-[:STEERS]->(p:Project)
MATCH (who:Person)
  WHERE (p)-[:OWNED_BY|STAKEHOLDER]->(who) OR (d)-[:DECIDED_BY]->(who)
RETURN coalesce(who.title, who.name) AS person, who.role AS role,
       count(DISTINCT CASE WHEN r.weight IS NOT NULL THEN d END) AS critical,
       collect(DISTINCT d.title) AS decisions,
       collect(DISTINCT p.name) AS projects
ORDER BY critical DESC, person;
