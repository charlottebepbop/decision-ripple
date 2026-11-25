// Who to tell about live decisions resting on $assumptions.
// One row per person. A decision that is critical under two of those
// assumptions counts once: the critical flag is folded per decision
// before the person is summed. 4-tell is unchanged and still counts
// per assumption.
MATCH (a:Assumption)<-[r:RESTS_ON]-(d:Decision {status: 'live'})
WHERE a.name IN $assumptions
MATCH (d)-[:STEERS]->(p:Project)
MATCH (who:Person)
  WHERE (p)-[:OWNED_BY|STAKEHOLDER]->(who) OR (d)-[:DECIDED_BY]->(who)
WITH who, d, max(CASE WHEN r.weight = 'critical' THEN 1 ELSE 0 END) AS critical
RETURN who.name AS person, who.role AS role, who.text AS text,
       sum(critical) AS critical,
       [t IN collect(CASE WHEN critical = 1 THEN d.title END) WHERE t IS NOT NULL] AS critical_decisions,
       [t IN collect(CASE WHEN critical = 0 THEN d.title END) WHERE t IS NOT NULL] AS other_decisions
ORDER BY critical DESC, person;
