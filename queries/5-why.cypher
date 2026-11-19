// Why: find decisions by the words in their notes, then pull in the graph around them.
MATCH (d:Decision)
SEARCH d IN (FULLTEXT INDEX decision_text FOR $term LIMIT 5)
OPTIONAL MATCH (d)-[:DECIDED_BY]->(who:Person)
OPTIONAL MATCH (d)-[:RESTS_ON]->(a:Assumption)
OPTIONAL MATCH (newer:Decision)-[:SUPERSEDES]->(d)
RETURN d.title AS decision, d.status AS status, d.date AS date,
       collect(DISTINCT who.name) AS decided_by,
       collect(DISTINCT a.name) AS rests_on,
       newer.title AS replaced_by;
